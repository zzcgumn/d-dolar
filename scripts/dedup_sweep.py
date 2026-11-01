#!/usr/bin/env python3
"""Finds likely-duplicate player names in a RawDB directory,
clusters them, and builds both a raw and a tentatively-deduplicated
partnership list -- see docs/dedup_sweep.md for what this writes
and the risks its deduped output always carries. Not part of the
d_dolar package's public API: no `[project.scripts]` entry, run
directly (after `pip install -e ".[dev]"`, this doc's own stated
prerequisite), matching scripts/build_dds3.sh's role as operational
tooling over the library rather than inside it."""

import argparse
import csv
import os
import time
from multiprocessing import Pool
from pathlib import Path

from d_dolar.analysis.dedup import canonical_aliases, cluster_names, name_frequencies
from d_dolar.analysis.name_similarity import candidate_pairs, distinct_names
from d_dolar.analysis.partnerships import enumerate_partnerships
from d_dolar.rawdb.loader import load_joined_boards

_NAMES: list[str] = []
_THRESHOLD: float = 0.85


def _init_worker(names: list[str], threshold: float) -> None:
    global _NAMES, _THRESHOLD
    _NAMES = names
    _THRESHOLD = threshold


def _process_chunk(bounds: tuple[int, int]) -> list[tuple[str, str, float]]:
    start, stop = bounds
    return candidate_pairs(_NAMES, start, stop, _THRESHOLD)


def run_sweep(
    names: list[str], threshold: float, chunk_width: int, workers: int
) -> list[tuple[str, str, float]]:
    """The parallel orchestration itself -- deliberately NOT part
    of d_dolar.analysis.name_similarity, which only provides the
    single-chunk-at-a-time candidate_pairs primitive. Splits
    `names` into fixed-width index-range chunks and runs them
    across a worker pool; chunk results concatenate directly, with
    no merge/de-dup step, by candidate_pairs' own design."""
    n = len(names)
    chunks = [(start, min(start + chunk_width, n)) for start in range(0, n, chunk_width)]
    candidates: list[tuple[str, str, float]] = []
    with Pool(processes=workers, initializer=_init_worker, initargs=(names, threshold)) as pool:
        for result in pool.imap_unordered(_process_chunk, chunks):
            candidates.extend(result)
    return candidates


def write_candidates_csv(path: Path, candidates: list[tuple[str, str, float]]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name_a", "name_b", "score"])
        writer.writerows(sorted(candidates, key=lambda candidate: candidate[2], reverse=True))


def write_summary(
    path: Path,
    *,
    n_names: int,
    total_pairs: int,
    elapsed: float,
    candidates: list[tuple[str, str, float]],
    clusters: list[list[str]],
    aliases: dict[str, str],
    raw_count: int,
    deduped_count: int,
    show_largest: int,
    candidates_csv_name: str,
    raw_csv_name: str,
    deduped_csv_name: str,
) -> None:
    """Generated from THIS run's own numbers -- the caveat text and
    the two named risks are generic (true of the method itself),
    never an assertion that a specific group in THIS run is wrong:
    this script has not judged any group, it only lists the
    largest ones for a human to look at."""
    merge_groups = [members for members in clusters if len(members) > 1]
    largest = sorted(merge_groups, key=len, reverse=True)[:show_largest]

    with path.open("w") as f:
        f.write("# Deduplicated partnership list (UNVERIFIED)\n\n")
        f.write(
            "**Caveat -- read before trusting any number below.** This "
            f"deduplication was built automatically from `{candidates_csv_name}` "
            f"({len(candidates):,} name pairs scoring above the configured "
            "threshold from a `difflib`-based similarity sweep) by treating "
            "every candidate pair as a confirmed merge, with no human "
            "review. Two risks this carries:\n\n"
            "1. **Individual false-positive pairs.** A high `difflib` "
            "score does not guarantee two spellings are the same person "
            "-- only that they look similar as strings.\n"
            "2. **Transitive over-merging.** Names are merged by "
            "connected component, not just by direct pair: if A matches "
            "B and B matches C, A and C end up in the same merge group "
            "even if A and C were never compared directly and might not "
            "actually be the same person. A single bad edge can chain "
            "unrelated people together through a longer path -- inspect "
            "the largest groups below first, since that is where this "
            "is most likely to have happened (see docs/dedup_sweep.md "
            "for a real, confirmed example of this exact failure "
            "mode).\n\n"
            f"**This dedup should be checked** -- at minimum, skim the "
            f"largest merge groups below and the full "
            f"`{candidates_csv_name}` -- before treating "
            f"`{deduped_csv_name}` as a trustworthy partnership "
            f"definition. Until then, use `{raw_csv_name}` (no merging "
            "at all, just case/whitespace normalization) as the safe "
            "baseline.\n\n"
        )
        f.write("## Numbers\n\n")
        f.write(f"- Distinct names: {n_names:,}\n")
        f.write(f"- Total pairs in the full sweep: {total_pairs:,}\n")
        f.write(f"- Sweep wall-clock time: {elapsed:.1f}s\n")
        f.write(f"- Candidate pairs found: {len(candidates):,}\n")
        f.write(f"- Merge groups (components with > 1 member): {len(merge_groups):,}\n")
        f.write(f"- Names aliased to a canonical spelling: {len(aliases):,}\n")
        f.write(f"- Partnerships, no dedup (`{raw_csv_name}`): {raw_count:,}\n")
        f.write(f"- Partnerships, deduped (`{deduped_csv_name}`): {deduped_count:,}\n\n")
        f.write(
            f"## {show_largest} largest merge groups (inspect these "
            "first -- listed for review, not asserted to be wrong)\n\n"
        )
        for members in largest:
            canonical = next(member for member in members if member not in aliases)
            sample = ", ".join(sorted(members)[:20])
            suffix = ", ..." if len(members) > 20 else ""
            f.write(f"- **{len(members)} names**, canonical `{canonical}`: {sample}{suffix}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rawdb-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--threshold", type=float, default=0.85)
    parser.add_argument("--min-boards", type=int, default=1)
    parser.add_argument("--chunk-width", type=int, default=200)
    parser.add_argument("--workers", type=int, default=os.cpu_count())
    parser.add_argument("--show-largest", type=int, default=10)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    joined = load_joined_boards(args.rawdb_dir)
    names = distinct_names(joined)

    t0 = time.time()
    candidates = run_sweep(names, args.threshold, args.chunk_width, args.workers)
    elapsed = time.time() - t0

    write_candidates_csv(args.output_dir / "candidate_pairs_full_sweep.csv", candidates)

    frequency = name_frequencies(joined)
    clusters = cluster_names(candidates)
    aliases = canonical_aliases(clusters, frequency)

    raw = enumerate_partnerships(joined, min_boards=args.min_boards, aliases=None)
    deduped = enumerate_partnerships(joined, min_boards=args.min_boards, aliases=aliases)

    raw.write_csv(args.output_dir / "partnerships_raw.csv")
    deduped.write_csv(args.output_dir / "partnerships_deduped_unverified.csv")

    n = len(names)
    write_summary(
        args.output_dir / "partnerships_deduped_unverified.md",
        n_names=n,
        total_pairs=n * (n - 1) // 2,
        elapsed=elapsed,
        candidates=candidates,
        clusters=clusters,
        aliases=aliases,
        raw_count=raw.height,
        deduped_count=deduped.height,
        show_largest=args.show_largest,
        candidates_csv_name="candidate_pairs_full_sweep.csv",
        raw_csv_name="partnerships_raw.csv",
        deduped_csv_name="partnerships_deduped_unverified.csv",
    )

    print(f"wrote results to {args.output_dir}")


if __name__ == "__main__":
    main()
