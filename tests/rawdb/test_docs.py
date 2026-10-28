from pathlib import Path

REPO_ROOT = Path(__file__).parents[2]


def test_rawdb_schema_doc_lists_every_column() -> None:
    from d_dolar.rawdb.schema import (
        BOARDS_SCHEMA,
        DEALS_SCHEMA,
        EVENTS_SCHEMA,
        HANDS_SCHEMA,
    )

    doc = (REPO_ROOT / "docs" / "rawdb_schema.md").read_text()
    all_columns = {*EVENTS_SCHEMA, *DEALS_SCHEMA, *HANDS_SCHEMA, *BOARDS_SCHEMA}
    missing = [c for c in sorted(all_columns) if c not in doc]
    assert not missing, f"docs/rawdb_schema.md is missing columns: {missing}"


def test_rawdb_import_spec_names_the_excluded_files() -> None:
    spec = (REPO_ROOT / "specs" / "rawdb-import.md").read_text()
    for excluded in ("all.csv", "RawData.csv", "ProcessedBoards.csv", "ProcessedDeals.csv"):
        assert excluded in spec
