import pytest
from src.model.infer_llama import parse_label


@pytest.mark.parametrize(
    "text, expected",
    [
        ("positive", "positive"),
        ("Etiqueta: neutral", "neutral"),
        ("This is negative.", "negative"),
        ("POSITIVE!!!", "positive"),
        ("neg", "negative"),   
        ("", "neutral"),
        (None, "neutral"),
    ],
)
def test_parse_label(text, expected):
    assert parse_label(text) == expected
