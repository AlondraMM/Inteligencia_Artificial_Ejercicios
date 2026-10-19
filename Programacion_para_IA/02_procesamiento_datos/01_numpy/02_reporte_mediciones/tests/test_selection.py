from pathlib import Path

import numpy as np
import pytest

from measurements.processing import load_readings
from measurements.selection import select_warm_rounds

DATA_DIR = Path(__file__).resolve().parents[2] / "datos"


def test_reference_selection_includes_exact_threshold_and_all_room_columns():
    readings = load_readings(DATA_DIR / "readings.csv")
    selected = select_warm_rounds(readings, 27)
    np.testing.assert_array_equal(selected, [[27, 29, 25], [28, 30, 26], [29, 31, 27]])
    assert selected.shape == (3, 3)


def test_no_matches_preserves_three_columns():
    readings = load_readings(DATA_DIR / "readings.csv")
    selected = select_warm_rounds(readings, 100)
    assert selected.shape == (0, 3)
    assert selected.dtype == readings.dtype


def test_selection_is_independent_and_preserves_input():
    readings = np.array([[29.0, 31.0, 27.0], [22.0, 24.0, 20.0], [27.0, 29.0, 25.0]])
    original = readings.copy()
    selected = select_warm_rounds(readings, 27)
    np.testing.assert_array_equal(selected, [[29, 31, 27], [27, 29, 25]])
    assert not np.shares_memory(selected, readings)
    selected[0, :] = -100
    np.testing.assert_array_equal(readings, original)


def test_single_matching_round_stays_two_dimensional():
    selected = select_warm_rounds(np.array([[27.0, 29.0, 25.0]]), 27)
    assert selected.shape == (1, 3)


@pytest.mark.parametrize(
    "readings",
    [
        np.array(27.0),
        np.array([27.0, 29.0, 25.0]),
        np.ones((2, 2)),
        np.ones((2, 4)),
        np.ones((2, 3, 1)),
        np.empty((0, 3)),
    ],
)
def test_invalid_shapes_are_rejected(readings):
    with pytest.raises(ValueError):
        select_warm_rounds(readings, 27)


@pytest.mark.parametrize("value", [np.nan, np.inf, -np.inf])
@pytest.mark.parametrize("room", [0, 1, 2])
def test_nonfinite_values_are_rejected_even_in_unselected_rounds(value, room):
    readings = np.array([[22.0, 24.0, 20.0], [27.0, 29.0, 25.0]])
    readings[0, room] = value
    with pytest.raises(ValueError, match="finite readings"):
        select_warm_rounds(readings, 27)


@pytest.mark.parametrize("threshold", [np.nan, np.inf, -np.inf])
def test_nonfinite_thresholds_are_rejected(threshold):
    with pytest.raises(ValueError, match="finite threshold"):
        select_warm_rounds(np.array([[27.0, 29.0, 25.0]]), threshold)
