"""Explicit Polars schemas for bridge-deals-ingest's RawDB CSV output.

Column order matches each real CSV's header exactly, so ``schema=`` also
pins column order: an upstream header reorder becomes a loud failure
rather than silently mismatched columns.
"""

import polars as pl

# polars has no public name for "a dtype, either as a class (pl.Int32) or an
# instance (pl.Categorical())" -- polars._typing.PolarsDataType is that, but
# it is a private module. This is its public equivalent.
_PolarsDataType = pl.DataType | type[pl.DataType]

EVENTS_SCHEMA: dict[str, _PolarsDataType] = {
    "EventUID": pl.Int32,
    "MatchID": pl.Int32,
    "EventName": pl.String,
    "MatchName": pl.String,
    "EventLocation": pl.String,
    "MatchDate": pl.String,
    "ScoringForm": pl.String,
    "Tables": pl.Int16,
    "FilePath": pl.String,
}

DEALS_SCHEMA: dict[str, _PolarsDataType] = {
    "DealUID": pl.Int32,
    "HandUID": pl.Int32,
    "EventUID": pl.Int32,
    "MatchID": pl.Int32,
    "SourceType": pl.Categorical(),
    "DealNum": pl.Int16,
    "Dealer": pl.Categorical(),
    "Vulnerability": pl.Categorical(),
    "Hands": pl.String,
    # Unreliable passthrough from the source file's own "DDS" field (EBL/WBF
    # JSON only); null for every other source. Not to be confused with
    # hands.csv's DD_<seat>_<strain> columns below.
    "DDS": pl.String,
    "DealerValidation": pl.Categorical(),
    "VulValidation": pl.Categorical(),
}

_SUITS = ("S", "H", "D", "C")
_SEATS = ("N", "E", "S", "W")
_DD_SEATS = ("W", "N", "E", "S")
_DD_STRAINS = ("N", "S", "H", "D", "C")

HANDS_SCHEMA: dict[str, _PolarsDataType] = {
    "HandUID": pl.Int32,
    "Dealer": pl.Categorical(),
    "Vulnerability": pl.Categorical(),
    "W_Hand": pl.String,
    "N_Hand": pl.String,
    "E_Hand": pl.String,
    "S_Hand": pl.String,
}
for _seat in _SEATS:
    for _suit in _SUITS:
        HANDS_SCHEMA[f"{_seat}_Length_{_suit}"] = pl.Int8
    for _suit in _SUITS:
        HANDS_SCHEMA[f"{_seat}_HCP_{_suit}"] = pl.Int8
    HANDS_SCHEMA[f"{_seat}_Total_HCP"] = pl.Int8
    HANDS_SCHEMA[f"{_seat}_Controls"] = pl.Int8
    HANDS_SCHEMA[f"{_seat}_Pattern"] = pl.String
    HANDS_SCHEMA[f"{_seat}_Shape"] = pl.String
HANDS_SCHEMA["Hands"] = pl.String
for _seat in _DD_SEATS:
    for _strain in _DD_STRAINS:
        HANDS_SCHEMA[f"DD_{_seat}_{_strain}"] = pl.Int8
HANDS_SCHEMA["ParScoreNS"] = pl.Int16
HANDS_SCHEMA["ParContracts"] = pl.String

BOARDS_SCHEMA: dict[str, _PolarsDataType] = {
    "BoardUID": pl.Int32,
    "DealUID": pl.Int32,
    # Confirmed free-text in the wild (a real row held a full match
    # description, not a table label) -- not a small fixed domain.
    "TableID": pl.String,
    "SourceType": pl.Categorical(),
    "North": pl.String,
    "East": pl.String,
    "South": pl.String,
    "West": pl.String,
    "Declarer": pl.Categorical(),
    # Unbounded shape ("AP", "4DX", "7NXX", ...) -- not a small fixed domain.
    "Contract": pl.String,
    "TricksMade": pl.Int8,
    "RawScoreNS": pl.Int16,
    "Auction": pl.String,
    "Lead": pl.String,
    "Play": pl.String,
    "PlayEncoding": pl.Categorical(),
    "Claim": pl.Int8,
    "BiddingMD": pl.String,
    "Commentary": pl.String,
}
