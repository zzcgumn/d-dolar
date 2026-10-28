from pathlib import Path

REPO_ROOT = Path(__file__).parents[1]


def test_dds3_spec_names_the_pinned_commit() -> None:
    spec = (REPO_ROOT / "specs" / "dds3-dependency.md").read_text()
    assert "cd953c24a68cb8117bff4fcfd1807ad18a197f6c" in spec
    assert "v3.1.1" in spec
