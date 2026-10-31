# Finding and tentatively merging likely-duplicate names

`scripts/dedup_sweep.py` runs the full likely-duplicate-name
discovery pipeline against a RawDB directory: a chunked,
parallelized similarity sweep
(`d_dolar.analysis.name_similarity.distinct_names`/`candidate_pairs`),
connected-components clustering and canonical-spelling selection
(`d_dolar.analysis.dedup`), and a before/after partnership count via
`d_dolar.analysis.partnerships.enumerate_partnerships`. It is
operational tooling built on top of the library, not part of
`d_dolar`'s own public API — see `specs/name-similarity.md`'s and
`specs/partnerships.md`'s "Out of scope" sections, both of which
name "no CLI" and "no actual parallel execution" as deliberate
library non-goals that this script exists precisely to not violate.

## Prerequisites

`d-dolar` installed (`pip install -e ".[dev]"`). No other
dependencies — this script is pure Python stdlib (`argparse`,
`csv`, `multiprocessing`) plus the already-installed `polars`.

## Run

```bash
python scripts/dedup_sweep.py \
  --rawdb-dir /path/to/your/RawDB \
  --output-dir /path/to/write/results
```

Flags (all optional except the two above):

| Flag | Default | Meaning |
| --- | --- | --- |
| `--threshold` | `0.85` | Minimum `name_similarity` score to count as a candidate pair. |
| `--min-boards` | `1` | Passed through to `enumerate_partnerships`. |
| `--chunk-width` | `200` | Names per sweep chunk — affects parallelism granularity, not the result. |
| `--workers` | `os.cpu_count()` | Worker processes for the sweep. |
| `--show-largest` | `10` | How many of the largest merge groups the summary report lists for review. |

## What it writes, into `--output-dir`

- `candidate_pairs_full_sweep.csv` — every name pair scoring `>=
  --threshold`, as `name_a,name_b,score`.
- `partnerships_raw.csv` — `enumerate_partnerships` with no merging
  beyond case/whitespace normalization. **The safe baseline.**
- `partnerships_deduped_unverified.csv` — the same, but with every
  candidate pair's connected component merged to one canonical
  spelling via `enumerate_partnerships`' `aliases` parameter.
- `partnerships_deduped_unverified.md` — a caveat report generated
  from the run's own numbers, always stating the risks below and
  listing the `--show-largest` largest merge groups for manual
  inspection.

## Known risks the deduped output always carries

1. **Individual false-positive pairs.** A high `difflib` score
   means two spellings look similar as strings, not that they are
   confirmed to be the same person — see `specs/name-similarity.md`'s
   own `WELKER JACINT`/`WELKER KATALIN` example (same surname, real
   different people, scoring `0.741`, i.e. below this tool's default
   threshold, but the same shape of false positive can occur above
   it too on a larger, messier real dataset).
2. **Transitive over-merging.** Merging by connected component (not
   just by direct pair) means a chain of individually-plausible
   pairs can pull in names that were never compared to each other
   directly. **This is not hypothetical.** Running this exact
   pipeline against a real ~2M-board RawDB dataset produced a
   427-name merge group canonicalized as `COHEN` — purely because
   that spelling happened to occur most often in the real data —
   that in fact chains together dozens of unrelated short names
   (`HARRIS`, `ZHANG`, `MARTIN`, `YUAN`, `HANS`, `LIN`, `IVAN`,
   `TAN`, `RYAN`, `JAN`, `WANG`, `CHEN`, and more), because short
   strings score deceptively high pairwise under `difflib` and a
   chain only needs one weak link at a time to keep growing.
3. **Run-to-run nondeterminism, confirmed by running this exact
   pipeline twice against the same real dataset.** `distinct_names`
   deduplicates raw spellings that are pure case/whitespace variants
   of each other (e.g. a real dataset's `"ERKAN"` and `"ERKAN "`,
   both already-confirmed to exist side by side) down to one
   representative per normalized name, but which raw spelling
   survives as that representative is not guaranteed to be the same
   across separate runs — only the final list's *order* is
   documented as deterministic, not the choice of survivor on a
   collision (see `specs/name-similarity.md`). Two full runs of this
   script against the identical real dataset, same `--threshold`,
   same `--chunk-width`, same `--workers`, produced the *same*
   10,030 candidates, the *same* 3,149 merge groups (down to the
   427-member group above), and yet a **different** deduped
   partnership count (24,449 vs. 24,468) — because `aliases` is
   applied via an exact raw-string match
   (`enumerate_partnerships`' own `aliases`-before-`normalize`
   ordering), so a row recorded under whichever case/whitespace
   variant was *not* chosen as that run's representative is never
   substituted by the alias map, even though `enumerate_partnerships`'
   own `normalize=True` step still folds it to the same lowercase
   form afterward. The practical effect: the exact deduped count can
   drift slightly run to run on the same data, even though every run
   is internally self-consistent. Not fixed here — this plan's scope
   was packaging the already-validated method, not improving it; see
   "Not built here" below.

**Always treat `partnerships_deduped_unverified.csv` as a draft, not
a result**, until the largest groups in
`partnerships_deduped_unverified.md` (and ideally the full candidate
list) have been reviewed. Once you have a confirmed, human-curated
set of corrections, apply them directly via
`enumerate_partnerships`' own `aliases` parameter — this script's
automatic clustering is a starting point for that review, not a
substitute for it.

## Not built here

- Fixing the over-merging failure mode itself (e.g. a
  minimum-name-length guard on candidate pairs, or a stricter
  clustering rule) — see `specs/name-similarity.md`'s and
  `specs/partnerships.md`'s own "Out of scope" sections.
- Fixing risk 3's run-to-run nondeterminism (e.g. giving
  `distinct_names` a documented, deterministic collision tie-break
  instead of "first-seen") — a separate, later concern.
- A `pip install`-exposed console command — run the script directly.
