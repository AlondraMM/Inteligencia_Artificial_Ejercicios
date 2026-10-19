import csv
import json
import sys

import numpy as np
import pytest
import torch
from PIL import Image
from torch.utils.data import TensorDataset

import main as app
from data_lab.inspection import collect_samples, image_transform, label_summary


def test_image_conversion_preserves_channels_and_scales_pixels():
    pixels = np.array([[[0, 127, 255], [255, 0, 127]]], dtype=np.uint8)
    result = image_transform()(Image.fromarray(pixels))
    assert result.shape == (3, 1, 2)
    assert result.dtype == torch.float32
    expected = torch.tensor([[[0, 255]], [[127, 0]], [[255, 127]]]) / 255
    torch.testing.assert_close(result, expected)
    np.testing.assert_array_equal(pixels[0, 0], [0, 127, 255])


@pytest.mark.parametrize("batch_size", [1, 4, 20])
def test_collection_preserves_order_pairs_and_short_last_batch(batch_size):
    images = torch.arange(12 * 3 * 2 * 2, dtype=torch.float32).reshape(12, 3, 2, 2)
    labels = torch.arange(12, dtype=torch.int64) % 3
    selected_images, selected_labels = collect_samples(
        TensorDataset(images, labels), limit=10, batch_size=batch_size
    )
    torch.testing.assert_close(selected_images, images[:10])
    torch.testing.assert_close(selected_labels, labels[:10])
    summary = label_summary(selected_labels, ["class_a", "class_b", "class_c"])
    assert [row["count"] for row in summary] == [4, 3, 3]
    assert [row["proportion"] for row in summary] == pytest.approx([0.4, 0.3, 0.3])


@pytest.mark.parametrize("limit,batch_size", [(0, 4), (4, 4), (2, 0)])
def test_invalid_collection_arguments(limit, batch_size):
    dataset = TensorDataset(torch.zeros(3, 3, 2, 2), torch.zeros(3, dtype=torch.int64))
    with pytest.raises(ValueError):
        collect_samples(dataset, limit, batch_size)


def test_counts_and_proportions_include_absent_classes():
    result = label_summary(
        torch.tensor([0, 0, 2, 2, 2]), ["class_a", "class_b", "class_c"]
    )
    assert [row["class_id"] for row in result] == [0, 1, 2]
    assert [row["class_name"] for row in result] == ["class_a", "class_b", "class_c"]
    assert [row["count"] for row in result] == [2, 0, 3]
    assert sum(row["count"] for row in result) == 5
    assert [row["proportion"] for row in result] == pytest.approx([0.4, 0.0, 0.6])
    assert all(isinstance(row["proportion"], float) for row in result)
    assert sum(row["proportion"] for row in result) == pytest.approx(1.0)


def test_limit_can_change_class_counts_and_proportion_denominator():
    dataset = TensorDataset(torch.zeros(5, 3, 2, 2), torch.tensor([0, 0, 2, 2, 2]))
    _, first_two = collect_samples(dataset, limit=2, batch_size=2)
    _, first_five = collect_samples(dataset, limit=5, batch_size=2)
    class_names = ["class_a", "class_b", "class_c"]
    short_summary = label_summary(first_two, class_names)
    full_summary = label_summary(first_five, class_names)
    assert [row["count"] for row in short_summary] == [2, 0, 0]
    assert [row["proportion"] for row in short_summary] == [1.0, 0.0, 0.0]
    assert [row["count"] for row in full_summary] == [2, 0, 3]
    assert [row["proportion"] for row in full_summary] == pytest.approx([0.4, 0, 0.6])


@pytest.mark.parametrize(
    "labels",
    [
        torch.tensor([], dtype=torch.int64),
        torch.tensor([[0, 1]]),
        torch.tensor([0.5, 1.0]),
        torch.tensor([-1, 0]),
        torch.tensor([0, 2]),
    ],
)
def test_invalid_labels_are_rejected(labels):
    with pytest.raises(ValueError):
        label_summary(labels, ["class_a", "class_b"])


def test_application_exports_matching_arrays_and_counts(tmp_path, monkeypatch):
    images = (
        torch.arange(10 * 3 * 2 * 2, dtype=torch.float32).reshape(10, 3, 2, 2) / 120
    )
    labels = torch.tensor([0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
    dataset = TensorDataset(images, labels)
    dataset.classes = ["class_a", "class_b"]
    monkeypatch.setattr(app, "CIFAR10", lambda **kwargs: dataset)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--limit",
            "10",
            "--batch-size",
            "4",
            "--output-dir",
            str(tmp_path),
        ],
    )
    assert app.main() == 0
    np.testing.assert_array_equal(np.load(tmp_path / "images.npy"), images.numpy())
    np.testing.assert_array_equal(np.load(tmp_path / "labels.npy"), labels.numpy())
    report = json.loads((tmp_path / "report.json").read_text())
    assert report["samples_used"] == 10
    assert report["image_shape"] == [10, 3, 2, 2]
    with (tmp_path / "class_counts.csv").open() as source:
        rows = list(csv.DictReader(source))
    assert list(rows[0]) == ["class_id", "class_name", "count", "proportion"]
    assert sum(int(row["count"]) for row in rows) == 10
    assert [float(row["proportion"]) for row in rows] == pytest.approx([0.5, 0.5])
    assert sum(float(row["proportion"]) for row in rows) == pytest.approx(1.0)


def test_missing_dataset_does_not_create_output(tmp_path, monkeypatch):
    output = tmp_path / "output"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--data-dir",
            str(tmp_path / "missing"),
            "--output-dir",
            str(output),
        ],
    )
    assert app.main() == 1
    assert not output.exists()
