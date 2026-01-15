from pathlib import Path
import pandas as pd
import pytest

from src.preprocessing.clean import clean_text, stars_to_label, latest_parquet


def test_clean_text_basic():
    assert clean_text("  hola   mundo ") == "hola mundo"
    assert clean_text("") == ""
    assert clean_text(None) == ""


@pytest.mark.parametrize(
    "stars, expected",
    [(1, "negative"), (2, "negative"), (3, "neutral"), (4, "positive"), (5, "positive")],
)
def test_stars_to_label(stars, expected):
    assert stars_to_label(stars) == expected


def test_latest_parquet(tmp_path: Path):
    p1 = tmp_path / "a.parquet"
    p2 = tmp_path / "b.parquet"

    pd.DataFrame({"x": [1]}).to_parquet(p1, index=False)
    pd.DataFrame({"x": [2]}).to_parquet(p2, index=False)

    p1.touch()
    p2.touch()

    assert latest_parquet(tmp_path).name in {"a.parquet", "b.parquet"}
