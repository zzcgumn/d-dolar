# specs/

The design record: the contract each statistic implements, and why, written
so a coding agent — human or machine — can change behaviour correctly. A spec
is read *before* behaviour changes; it is not a summary written after the
fact.

- [`rawdb-import.md`](rawdb-import.md) — how a `bridge-deals-ingest` RawDB
  directory gets into a typed, validated Polars frame.
- [`dds3-dependency.md`](dds3-dependency.md) — the vendored DDS 3.1.1
  Python module, how it's built, and what's guaranteed about it.

D-dolar and the two sibling double-dummy-based defence statistics
themselves are not written up yet (this branch doesn't yet have
`calculate_d_dolar`'s `specs/d-dolar.md` merged in).
