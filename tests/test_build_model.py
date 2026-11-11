"""Regression tests for TTC source schema normalization."""

import pandas as pd

from src.build_model import normalize_columns


def test_canonical_columns_win_over_aliases():
    frame = pd.DataFrame({
        "Min Delay": [5], "Delay": [99], "Delay Min": [42],
        "Min Gap": [3], "Gap": [88],
    })
    normalized = normalize_columns(frame)
    assert normalized.columns.is_unique
    assert normalized["min_delay"].iloc[0] == 5
    assert normalized["min_gap"].iloc[0] == 3


def test_multiple_aliases_do_not_create_duplicate_fields():
    frame = pd.DataFrame({
        "Delay": [3], "Delay Min": [4], "Gap": [5], "Gap Min": [6],
    })
    normalized = normalize_columns(frame)
    assert normalized.columns.is_unique
    assert normalized["min_delay"].iloc[0] == 3
    assert normalized["min_gap"].iloc[0] == 5


def test_single_alias_maps_to_expected_field():
    normalized = normalize_columns(pd.DataFrame({"Delay Min": [12], "Gap Min": [2]}))
    assert list(normalized.columns) == ["min_delay", "min_gap"]
