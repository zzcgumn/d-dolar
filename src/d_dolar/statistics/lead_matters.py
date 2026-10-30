"""The lead-matters statistic: could any legal choice of opening
lead have changed the double-dummy outcome, or was the leader's
choice irrelevant either way."""

from d_dolar.statistics._lead_choices import lead_choices


def lead_matters(hands: str, declarer: str | None, contract: str | None) -> bool | None:
    """True if at least two legal opening leads give different
    double-dummy outcomes; False if every choice gives the same
    outcome (no lead could have changed anything); None under
    lead_choices' own None condition."""
    choices = lead_choices(hands, declarer, contract)
    if choices is None:
        return None
    _, defender_tricks = choices
    return len(set(defender_tricks)) > 1
