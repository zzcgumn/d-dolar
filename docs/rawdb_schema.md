# RawDB schema reference

The caller's guide to the 4 files `d_dolar.rawdb` reads from a
[bridge-deals-ingest](https://github.com/ureshvahalia/bridge-deals-ingest)
`RawDB` output directory: `events.csv`, `deals.csv`, `hands.csv`,
`boards.csv`. See [`specs/rawdb-import.md`](../specs/rawdb-import.md) for
why only these 4 of the 8 files RawDB produces are read, and the
invariants `d_dolar.rawdb.validate.check_invariants` enforces on them.

Column order below matches each real CSV's header exactly, and matches
`d_dolar.rawdb.schema`'s `EVENTS_SCHEMA`/`DEALS_SCHEMA`/`HANDS_SCHEMA`/
`BOARDS_SCHEMA` dicts, which are the ground truth — this document restates
them for a human reader, not the other way round.

## Formats and conventions worth knowing before reading the tables

**`Hands`** (`deals.csv`, `hands.csv`): PBN format, e.g.
`"W:AK3.K4.AKQT8.J75 T964.T92.J7.AT82 J85.AJ863.64.K96 Q72.Q75.9532.Q43"` —
`<first-seat>:<hand> <hand> <hand> <hand>`, the 4 hands listed clockwise
starting from `<first-seat>`, each hand `S.H.D.C`, highest card first,
an empty segment for a void suit. `deals.Hands` and `hands.Hands` are the
same string by construction; `d_dolar.rawdb.loader.load_joined_boards`
asserts they agree rather than silently keeping one.

**`DD_<seat>_<strain>`** (`hands.csv` only, 20 columns, seats `W N E S` ×
strains `N S H D C`, `N` meaning notrump): tricks for `<seat>` declaring
`<strain>`, computed by `endplay.dds.calc_all_tables`. A partnership's two
members are often, but **not reliably**, equal here (`DD_N_x == DD_S_x`,
`DD_E_x == DD_W_x`) — do not treat this as an invariant. Checked against
the full RawDB `hands.csv`: 24.3% of hands have at least one strain where
`DD_N_x != DD_S_x`, 24.2% have at least one strain where `DD_E_x !=
DD_W_x`, and 42.4% have at least one such mismatch on either side —
nowhere near rare enough to be a computational edge case. `check_invariants`
does not enforce this identity.

**`DDS`** (`deals.csv` only): an *unrelated*, unreliable column — **do not
confuse it with `DD_<seat>_<strain>`**. It is the literal `DDS` field
copied verbatim from the source file, only ever populated for EBL/WBF JSON
sources, and `null` for every other source. It is not validated, not in a
guaranteed format, and not read by anything in `d_dolar.rawdb`.

**`ParScoreNS`**: NS-perspective par score, from `endplay.dds.par`.
**`ParContracts`**: space-separated contracts making that score, e.g.
`"5DEx-2 5DWx-2"` — grammar `<level><strain><declarer>[x|xx][+n|-n|=]`,
several when more than one contract makes par.

**`Pattern`/`Shape`/`HCP_<suit>`/`Total_HCP`/`Controls`** (`hands.csv`, one
set per seat): `Pattern` is `S-H-D-C` suit lengths, dash-joined in suit
order (e.g. `"4-3-3-3"`); `Shape` is the same 4 lengths sorted descending,
dot-joined (e.g. `"4.3.3.3"`). HCP: A=4 K=3 Q=2 J=1. Controls: A=2 K=1.
`check_invariants` enforces: the 4 suit-HCP values sum to `Total_HCP`; the
4 seats' `Total_HCP` sum to 40 (the deck's total); a seat's 4 suit lengths
sum to 13; a suit's 4 seat-lengths also sum to 13.

**`Vulnerability`**: `Z` (none) `N` `E` `B` (both) `X` (unknown).
**`Dealer`/`Declarer`**: `N`/`E`/`S`/`W`. **Note**: `Declarer` is *not*
reliably empty when `Contract == "AP"` (all pass) — in the real data,
roughly half of all-pass boards have it filled in anyway, a source quirk;
`check_invariants` does not assume otherwise.

**`TricksMade`**: 0–13, null if unknown. **`RawScoreNS`**: NS-perspective,
signed, null when only tricks (not score) are known. **`TableID`** and
**`Contract`** are free-text `String`, not a small fixed domain — a real
`TableID` was found holding a full match description rather than a table
label, and `Contract` ranges over `"AP"` and every leveled/doubled shape.
**`Lead`/`Play`**: card codes (`"S6"`, `"SJ_SQ_S3_..."`); `Play` is an
empty string, not null, when not recorded. **`Auction`**: bids
dash-joined (`"P-P-P-2N-P-3D..."`), `X`/`XX` for double/redouble.

**Nulls**: every CSV field is read with `null_values=[""]`; an empty
string becomes a genuine null for every column except where the format
itself uses `""` to mean something other than "unknown" (`Play`'s "not
recorded").

## Column reference

### `events.csv`

| Column | Dtype |
| --- | --- |
| `EventUID` | `Int32` |
| `MatchID` | `Int32` |
| `EventName` | `String` |
| `MatchName` | `String` |
| `EventLocation` | `String` |
| `MatchDate` | `String` |
| `ScoringForm` | `String` |
| `Tables` | `Int16` |
| `FilePath` | `String` |

### `deals.csv`

| Column | Dtype |
| --- | --- |
| `DealUID` | `Int32` |
| `HandUID` | `Int32` |
| `EventUID` | `Int32` |
| `MatchID` | `Int32` |
| `SourceType` | `Categorical` |
| `DealNum` | `Int16` |
| `Dealer` | `Categorical` |
| `Vulnerability` | `Categorical` |
| `Hands` | `String` |
| `DDS` | `String` |
| `DealerValidation` | `Categorical` |
| `VulValidation` | `Categorical` |

### `hands.csv`

| Column | Dtype |
| --- | --- |
| `HandUID` | `Int32` |
| `Dealer` | `Categorical` |
| `Vulnerability` | `Categorical` |
| `W_Hand` | `String` |
| `N_Hand` | `String` |
| `E_Hand` | `String` |
| `S_Hand` | `String` |
| `N_Length_S` | `Int8` |
| `N_Length_H` | `Int8` |
| `N_Length_D` | `Int8` |
| `N_Length_C` | `Int8` |
| `N_HCP_S` | `Int8` |
| `N_HCP_H` | `Int8` |
| `N_HCP_D` | `Int8` |
| `N_HCP_C` | `Int8` |
| `N_Total_HCP` | `Int8` |
| `N_Controls` | `Int8` |
| `N_Pattern` | `String` |
| `N_Shape` | `String` |
| `E_Length_S` | `Int8` |
| `E_Length_H` | `Int8` |
| `E_Length_D` | `Int8` |
| `E_Length_C` | `Int8` |
| `E_HCP_S` | `Int8` |
| `E_HCP_H` | `Int8` |
| `E_HCP_D` | `Int8` |
| `E_HCP_C` | `Int8` |
| `E_Total_HCP` | `Int8` |
| `E_Controls` | `Int8` |
| `E_Pattern` | `String` |
| `E_Shape` | `String` |
| `S_Length_S` | `Int8` |
| `S_Length_H` | `Int8` |
| `S_Length_D` | `Int8` |
| `S_Length_C` | `Int8` |
| `S_HCP_S` | `Int8` |
| `S_HCP_H` | `Int8` |
| `S_HCP_D` | `Int8` |
| `S_HCP_C` | `Int8` |
| `S_Total_HCP` | `Int8` |
| `S_Controls` | `Int8` |
| `S_Pattern` | `String` |
| `S_Shape` | `String` |
| `W_Length_S` | `Int8` |
| `W_Length_H` | `Int8` |
| `W_Length_D` | `Int8` |
| `W_Length_C` | `Int8` |
| `W_HCP_S` | `Int8` |
| `W_HCP_H` | `Int8` |
| `W_HCP_D` | `Int8` |
| `W_HCP_C` | `Int8` |
| `W_Total_HCP` | `Int8` |
| `W_Controls` | `Int8` |
| `W_Pattern` | `String` |
| `W_Shape` | `String` |
| `Hands` | `String` |
| `DD_W_N` | `Int8` |
| `DD_W_S` | `Int8` |
| `DD_W_H` | `Int8` |
| `DD_W_D` | `Int8` |
| `DD_W_C` | `Int8` |
| `DD_N_N` | `Int8` |
| `DD_N_S` | `Int8` |
| `DD_N_H` | `Int8` |
| `DD_N_D` | `Int8` |
| `DD_N_C` | `Int8` |
| `DD_E_N` | `Int8` |
| `DD_E_S` | `Int8` |
| `DD_E_H` | `Int8` |
| `DD_E_D` | `Int8` |
| `DD_E_C` | `Int8` |
| `DD_S_N` | `Int8` |
| `DD_S_S` | `Int8` |
| `DD_S_H` | `Int8` |
| `DD_S_D` | `Int8` |
| `DD_S_C` | `Int8` |
| `ParScoreNS` | `Int16` |
| `ParContracts` | `String` |

### `boards.csv`

| Column | Dtype |
| --- | --- |
| `BoardUID` | `Int32` |
| `DealUID` | `Int32` |
| `TableID` | `String` |
| `SourceType` | `Categorical` |
| `North` | `String` |
| `East` | `String` |
| `South` | `String` |
| `West` | `String` |
| `Declarer` | `Categorical` |
| `Contract` | `String` |
| `TricksMade` | `Int8` |
| `RawScoreNS` | `Int16` |
| `Auction` | `String` |
| `Lead` | `String` |
| `Play` | `String` |
| `PlayEncoding` | `Categorical` |
| `Claim` | `Int8` |
| `BiddingMD` | `String` |
| `Commentary` | `String` |
