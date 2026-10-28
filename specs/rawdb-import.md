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
| `ProcessedBoards.csv` | no | adds derived/validated auction columns, but drops boards with an unparseable auction — the wrong default for an import layer, which must not silently lose boards |
| `ProcessedDeals.csv` | no | `deals.csv` + `hands.csv`'s hand-derived columns, already joinable from the two files this package reads |

Loading only `boards`+`deals`+`hands`+`events` reads roughly a fifth of a
full RawDB directory's size, and keeps every board the other three files
would have dropped.

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
- every `boards.DealUID` exists in `deals.DealUID`, and every
  `deals.HandUID` exists in `hands.HandUID`

It deliberately does **not** check that `Declarer` is empty whenever
`Contract == "AP"` — real RawDB data violates that about as often as not
(a source quirk, confirmed by scanning the full `boards.csv`: 629 all-pass
boards with `Declarer` filled in against 642 with it empty).

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
last-updated: 2026-10-28
related-plans: import-raw-bridge-deals-csv
