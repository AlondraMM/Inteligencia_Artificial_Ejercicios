import numpy as np
import pandas as pd
import pytest

from titanic.analysis import (
    missing_age_by_class,
    numerical_arrays,
    prepare_passengers,
    survival_by_group,
)


@pytest.fixture
def small_table() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "PassengerId": [1, 2, 3],
            "Survived": [0, 1, 1],
            "Pclass": [3, 1, 1],
            "Sex": ["male", "female", "female"],
            "Age": [20.0, np.nan, 40.0],
            "SibSp": [0, 1, 0],
            "Parch": [0, 1, 0],
            "Fare": [7.0, 50.0, 60.0],
            "Embarked": ["S", "C", "C"],
        }
    )


def test_prepare_keeps_input_and_records_age_imputation(small_table: pd.DataFrame):
    before = small_table.copy(deep=True)
    prepared = prepare_passengers(small_table)
    pd.testing.assert_frame_equal(small_table, before)
    assert prepared["age_missing"].tolist() == [False, True, False]
    assert prepared["age_filled"].tolist() == [20.0, 30.0, 40.0]
    assert prepared["family_size"].tolist() == [1, 3, 1]


def test_grouped_rates_and_array_order(small_table: pd.DataFrame):
    prepared = prepare_passengers(small_table)
    summary = survival_by_group(prepared)
    assert summary["passengers"].sum() == 3
    assert summary.loc[summary["Pclass"] == 1, "survival_rate"].item() == 1.0
    features, labels = numerical_arrays(prepared)
    assert features.shape == (3, 4)
    assert labels.tolist() == [0, 1, 1]
    np.testing.assert_array_equal(features[1], [1.0, 30.0, 50.0, 3.0])


def test_missing_age_rates_preserve_original_indicator_after_imputation(small_table):
    prepared = prepare_passengers(small_table)
    before = prepared.copy(deep=True)
    assert prepared["age_filled"].notna().all()
    summary = missing_age_by_class(prepared)
    expected = pd.DataFrame(
        {
            "Pclass": [1, 3],
            "passengers": [2, 1],
            "missing_age_rate": [0.5, 0.0],
        }
    )
    pd.testing.assert_frame_equal(summary, expected)
    pd.testing.assert_frame_equal(prepared, before)
    assert summary["passengers"].sum() == len(prepared)
    assert summary["missing_age_rate"].between(0, 1).all()


def test_missing_age_rates_include_passengers_without_a_class():
    prepared = pd.DataFrame(
        {
            "Pclass": [1, 1, np.nan, np.nan, 3],
            "age_missing": [False, True, True, False, False],
            "age_filled": [20.0, 30.0, 30.0, 40.0, 22.0],
        }
    )
    summary = missing_age_by_class(prepared)
    expected = pd.DataFrame(
        {
            "Pclass": [1.0, 3.0, np.nan],
            "passengers": [2, 1, 2],
            "missing_age_rate": [0.5, 0.0, 0.5],
        }
    )
    pd.testing.assert_frame_equal(summary, expected)
    assert summary["passengers"].sum() == len(prepared)


@pytest.mark.parametrize("label", [0.5, 2, np.nan])
def test_invalid_labels_are_rejected_before_integer_conversion(small_table, label):
    invalid = small_table.astype({"Survived": float})
    invalid.loc[0, "Survived"] = label
    with pytest.raises(ValueError, match="Survived"):
        prepare_passengers(invalid)
    prepared = prepare_passengers(small_table).astype({"Survived": float})
    prepared.loc[0, "Survived"] = label
    with pytest.raises(ValueError, match="Survived"):
        numerical_arrays(prepared)


def test_missing_group_keys_do_not_remove_passengers(small_table):
    small_table.loc[0, "Sex"] = None
    summary = survival_by_group(prepare_passengers(small_table))
    assert summary["passengers"].sum() == len(small_table)
    assert summary.loc[summary["Sex"].isna(), "passengers"].item() == 1


@pytest.mark.parametrize("ids", [[1, 1, 3], [1, np.nan, 3]])
def test_invalid_passenger_ids_are_rejected(small_table, ids):
    small_table["PassengerId"] = ids
    with pytest.raises(ValueError, match="PassengerId"):
        prepare_passengers(small_table)


def test_no_observed_ages_are_rejected(small_table):
    small_table["Age"] = np.nan
    with pytest.raises(ValueError, match="At least one age"):
        prepare_passengers(small_table)


def test_nonfinite_features_are_rejected(small_table):
    prepared = prepare_passengers(small_table)
    prepared.loc[0, "Fare"] = np.inf
    with pytest.raises(ValueError, match="finite"):
        numerical_arrays(prepared)


def test_csv_and_cli_roundtrip(tmp_path):
    import subprocess
    import sys
    from pathlib import Path

    from titanic.analysis import load_passengers

    project_dir = Path(__file__).resolve().parents[1]
    csv_path = project_dir / "datasets" / "Titanic-Dataset.csv"
    passengers = load_passengers(csv_path)
    before = passengers.copy(deep=True)
    prepared = prepare_passengers(passengers)
    output = tmp_path / "outputs"
    subprocess.run(
        [sys.executable, str(project_dir / "main.py"), "--output-dir", str(output)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert passengers.shape == (891, 12)
    pd.testing.assert_frame_equal(passengers, before)
    pd.testing.assert_frame_equal(
        pd.read_csv(output / "passengers_prepared.csv"), prepared
    )
    pd.testing.assert_frame_equal(
        pd.read_csv(output / "survival_by_group.csv"), survival_by_group(prepared)
    )
    missing_ages = pd.read_csv(output / "missing_age_by_class.csv")
    pd.testing.assert_frame_equal(missing_ages, missing_age_by_class(prepared))
    assert missing_ages["passengers"].sum() == 891
    assert missing_ages["missing_age_rate"].between(0, 1).all()
    features, labels = numerical_arrays(prepared)
    np.testing.assert_array_equal(np.load(output / "features.npy"), features)
    np.testing.assert_array_equal(np.load(output / "labels.npy"), labels)
    assert features.dtype == np.float32
    assert labels.dtype == np.int64


def test_missing_columns_and_empty_csv_are_rejected(tmp_path, small_table):
    from titanic.analysis import load_passengers

    path = tmp_path / "passengers.csv"
    small_table.drop(columns="Age").to_csv(path, index=False)
    with pytest.raises(ValueError, match="Missing columns: Age"):
        load_passengers(path)
    small_table.iloc[:0].to_csv(path, index=False)
    with pytest.raises(ValueError, match="empty"):
        load_passengers(path)
