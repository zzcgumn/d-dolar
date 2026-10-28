# specs/

The design record: the contract each statistic implements, and why, written
so a coding agent — human or machine — can change behaviour correctly. A spec
is read *before* behaviour changes; it is not a summary written after the
fact.

- [`rawdb-import.md`](rawdb-import.md) — how a `bridge-deals-ingest` RawDB
  directory gets into a typed, validated Polars frame.
- [`d-dolar.md`](d-dolar.md) — the D-dolar base statistic (opening-lead
  optimality). The two sibling defence statistics are not written yet.
- [`dds3-dependency.md`](dds3-dependency.md) — the vendored DDS 3.1.1
  Python module, how it's built, and what's guaranteed about it.
