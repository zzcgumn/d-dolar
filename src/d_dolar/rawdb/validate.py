import polars as pl

DD_COLUMNS = [f"DD_{seat}_{strain}" for seat in "WNES" for strain in "NSHDC"]
SEATS = ("N", "E", "S", "W")
SUITS = ("S", "H", "D", "C")


def check_invariants(
    events: pl.DataFrame, deals: pl.DataFrame, hands: pl.DataFrame, boards: pl.DataFrame
) -> list[str]:
    violations: list[str] = []

    for col in DD_COLUMNS:
        bad = hands.filter(~pl.col(col).is_between(0, 13) & pl.col(col).is_not_null())
        if bad.height:
            violations.append(f"{col} out of [0, 13] in {bad.height} row(s)")

    bad = boards.filter(~pl.col("TricksMade").is_between(0, 13) & pl.col("TricksMade").is_not_null())
    if bad.height:
        violations.append(f"TricksMade out of [0, 13] in {bad.height} row(s)")

    for seat in SEATS:
        hcp_sum = sum(pl.col(f"{seat}_HCP_{s}") for s in SUITS)
        bad = hands.filter(hcp_sum != pl.col(f"{seat}_Total_HCP"))
        if bad.height:
            violations.append(f"{seat}_Total_HCP does not match its suit HCP sum in {bad.height} row(s)")

        len_sum = sum(pl.col(f"{seat}_Length_{s}") for s in SUITS)
        bad = hands.filter(len_sum != 13)
        if bad.height:
            violations.append(f"{seat}'s suit lengths do not sum to 13 in {bad.height} row(s)")

    for suit in SUITS:
        len_sum = sum(pl.col(f"{seat}_Length_{suit}") for seat in SEATS)
        bad = hands.filter(len_sum != 13)
        if bad.height:
            violations.append(f"suit {suit}'s 4 seat-lengths do not sum to 13 in {bad.height} row(s)")

    total_hcp = sum(pl.col(f"{seat}_Total_HCP") for seat in SEATS)
    bad = hands.filter(total_hcp != 40)
    if bad.height:
        violations.append(f"the 4 seats' Total_HCP do not sum to 40 in {bad.height} row(s)")

    dup = boards.filter(pl.col("BoardUID").is_duplicated())
    if dup.height:
        violations.append(f"duplicate BoardUID in {dup.height} row(s)")
    dup = deals.filter(pl.col("DealUID").is_duplicated())
    if dup.height:
        violations.append(f"duplicate DealUID in {dup.height} row(s)")
    dup = hands.filter(pl.col("HandUID").is_duplicated())
    if dup.height:
        violations.append(f"duplicate HandUID in {dup.height} row(s)")

    orphans = boards.join(deals.select("DealUID"), on="DealUID", how="anti")
    if orphans.height:
        violations.append(f"{orphans.height} boards row(s) reference a DealUID not in deals")
    orphans = deals.join(hands.select("HandUID"), on="HandUID", how="anti")
    if orphans.height:
        violations.append(f"{orphans.height} deals row(s) reference a HandUID not in hands")

    return violations
