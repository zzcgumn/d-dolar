# RawDB import

The contract `d_dolar.rawdb` implements: how a
[bridge-deals-ingest](https://github.com/ureshvahalia/bridge-deals-ingest)
`RawDB` output directory gets into a typed, validated Polars frame. Read
[`docs/rawdb_schema.md`](../docs/rawdb_schema.md) alongside this for the
column-by-column reference; this document is the *why*, that one is the
*what*.

## Behaviour & invariants

### Which files are read, and which are not

`bridge-deals-ingest` writes 8 CSV files to a RawDB directory.
`d_dolar.rawdb` reads exactly 4 of them:

| File | Read? | Why |
| --- | --- | --- |
| `boards.csv` | yes | one row per board per table: result, auction, play |
| `deals.csv` | yes | links a board to its hand (`HandUID`) and event |
| `hands.csv` | yes | unique hands with HCP/shape and the double-dummy tables + par this package exists to use |
| `events.csv` | yes | metadata only — event/match names, location, date |
| `all.csv` | no | a denormalized join of the above three plus validation flags; everything in it is derivable from them |
| `RawData.csv` | no | pre-dedup raw ingest; no `UID`s, no double-dummy data |
| `ProcessedBoards.csv` | no | a 1:1 enrichment of `boards.csv` adding derived/validated auction columns (verified: both have exactly 1,516,591 rows); not loaded because this package doesn't need those columns yet, not because of any row loss |
| `ProcessedDeals.csv` | no | `deals.csv` + `hands.csv`'s hand-derived columns, already joinable from the two files this package reads |

Loading only `boards`+`deals`+`hands`+`events` reads roughly a fifth of a
full RawDB directory's size.

**A note on row counts**: `boards.csv` contains quoted fields (`Commentary`,
`BiddingMD`) with embedded newlines, so `wc -l` overcounts it — it reports
1,970,074 lines, but the true row count (confirmed with both Polars and
Python's `csv` module) is 1,516,591. `deals.csv`, `hands.csv`, and
`events.csv` have no such fields; `wc -l` is accurate for those.

### What `load_joined_boards` guarantees

`d_dolar.rawdb.loader.load_joined_boards` returns `boards ⋈ deals
(DealUID) ⋈ hands (HandUID) ⋈ events (EventUID, MatchID)`, inner-joined,
as a single `pl.LazyFrame`. It raises `ValueError` if any row's
`deals.Hands` and `hands.Hands` disagree — they are the same PBN string by
construction, so a mismatch means something upstream is broken, not a
case to resolve silently by keeping one side.

The four single-file functions (`load_events`, `load_deals`, `load_hands`,
`load_boards`) each return a `pl.LazyFrame` over one RawDB file, scanned
with its explicit schema from `d_dolar.rawdb.schema` and
`null_values=[""]`. They stay lazy: nothing is materialized until a caller
collects.

### What `check_invariants` guarantees

`d_dolar.rawdb.validate.check_invariants(events, deals, hands, boards)`
takes the four **separately loaded and collected** frames — not the
joined result, deliberately: an inner join would silently drop a row
whose `DealUID`/`HandUID` has no match, which is exactly the defect this
function exists to surface. It returns a list of violation descriptions
(empty means clean), checking:

- every `DD_<seat>_<strain>` and `TricksMade` value is in `[0, 13]` when
  not null
- each seat's 4 suit-HCP values sum to that seat's `Total_HCP`
- the 4 seats' `Total_HCP` sum to 40
- each seat's 4 suit lengths sum to 13, and each suit's 4 seat-lengths
  also sum to 13
- `BoardUID`, `DealUID`, `HandUID` are each unique within their own table
- every `boards.DealUID` exists in `deals.DealUID`, `deals.HandUID` exists
  in `hands.HandUID`, and `deals.(EventUID, MatchID)` exists in
  `events.(EventUID, MatchID)`
- `deals.Vulnerability` and `hands.Vulnerability` are each one of
  `Z`/`N`/`E`/`B`/`X`; `deals.Dealer` and `hands.Dealer` are each one of
  `N`/`E`/`S`/`W`; `boards.Declarer` is one of `N`/`E`/`S`/`W` or null

It deliberately does **not** check that `Declarer` is empty whenever
`Contract == "AP"` — real RawDB data violates that about as often as not
(a source quirk, confirmed by scanning the full `boards.csv`: 629 all-pass
boards with `Declarer` filled in against 642 with it empty).

**A known real-data violation**: running `check_invariants` against the
full RawDB directory reports exactly one violation — 3 `boards.csv` rows
(`BoardUID` 990946, 1229835, 1229838, all `Contract == "AP"`) have
`Declarer == "s"` (lowercase), outside the `N`/`E`/`S`/`W` domain. This is
a genuine upstream data defect, not a bug in this package; `d_dolar.rawdb`
does not correct it.

**Two more real-data quirks in `Play`**, found while building the
second-defender-tricks-lost statistic, neither checked by
`check_invariants` (see `specs/second-defender-tricks-lost.md`'s "Out
of scope"): exactly 1 of the ~560,000 boards with any recorded `Play`
has a corrupted, structurally impossible play string (`BoardUID
770156`'s `Play` repeats the same 4-card block five times — 58 cards
from a 52-card deck); and 105 of those ~560,000 boards have a `Play`
whose first card does not match the separate `Lead` column's value.

**A fourth real-data quirk, in `Lead`**, found while running
`d_dolar_base` against the full RawDB (it previously raised an
uncaught `RuntimeError` from `dds3` on these rows instead of returning
`None`): of 1,028,505 boards with `Declarer`, `Contract`, and `Lead`
all present, 34,109 (~3.3%) have a `Lead` that the seat computed to be
the opening leader does not actually hold, per the `Hands` PBN string
(e.g. `BoardUID 1194011`: `Declarer = W`, so the leader is North, but
North's hand has no `D7`, which is the recorded `Lead`). Not checked
by `check_invariants` — same posture as the other three defects above.

### Null semantics

Every column is read with `null_values=[""]`: an empty CSV field becomes a
genuine Polars null, for every column, including numeric ones like
`RawScoreNS` and `TricksMade` which are legitimately unknown on some rows.
The one documented exception is `Play`: an empty string there means "not
recorded" by the source format itself, not "unknown" — it is kept as
`pl.String` and is never expected to be null.

## Out of scope

- Parsing `Auction`, `Play`, or `Hands` into structured bid or card
  sequences — every one of these stays the raw string from the CSV.
- The unreliable `DDS` string column in `deals.csv` (an unvalidated
  passthrough from EBL/WBF JSON sources only) is loaded as `pl.String` but
  never interpreted — not to be confused with `hands.csv`'s
  `DD_<seat>_<strain>` columns, which are this package's actual
  double-dummy data.
- Computing D-dolar or any other statistic — this package only gets
  validated board/deal/hand data into a Polars frame.

---
last-updated: 2026-10-29
related-plans: import-raw-bridge-deals-csv, second-defender-tricks-lost, d-dolar-lead-ownership-check
