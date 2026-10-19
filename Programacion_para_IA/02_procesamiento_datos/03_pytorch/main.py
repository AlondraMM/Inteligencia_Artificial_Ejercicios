"""Export a reproducible CIFAR-10 sample for later visualization."""

import argparse
import csv
import json
import logging
from pathlib import Path

import numpy as np
from torchvision.datasets import CIFAR10

from data_lab.inspection import collect_samples, image_transform, label_summary

PROJECT_DIR = Path(__file__).resolve().parent
logger = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect CIFAR-10 samples")
    parser.add_argument("--data-dir", type=Path, default=PROJECT_DIR / "data")
    parser.add_argument("--output-dir", type=Path, default=PROJECT_DIR / "outputs")
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--limit", type=int, default=64)
    parser.add_argument("--batch-size", type=int, default=16)
    args = parser.parse_args()
    if not 1 <= args.limit <= 10000:
        parser.error("--limit must be between 1 and 10000 for the test split")
    if args.batch_size <= 0:
        parser.error("--batch-size must be positive")
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    try:
        dataset = CIFAR10(
            root=args.data_dir,
            train=False,
            download=args.download,
            transform=image_transform(),
        )
        images, labels = collect_samples(dataset, args.limit, args.batch_size)
        counts = label_summary(labels, dataset.classes)
        report = {
            "dataset": "CIFAR-10",
            "split": "test",
            "dataset_size": len(dataset),
            "selection": "first samples in dataset order",
            "samples_used": len(labels),
            "batch_size": args.batch_size,
            "image_shape": list(images.shape),
            "image_dtype": str(images.dtype),
            "image_layout": "NCHW",
            "image_range": [float(images.min()), float(images.max())],
            "label_dtype": str(labels.dtype),
            "classes": dataset.classes,
        }
        args.output_dir.mkdir(parents=True, exist_ok=True)
        np.save(args.output_dir / "images.npy", images.numpy(), allow_pickle=False)
        np.save(args.output_dir / "labels.npy", labels.numpy(), allow_pickle=False)
        with (args.output_dir / "class_counts.csv").open(
            "w", encoding="utf-8", newline=""
        ) as destination:
            writer = csv.DictWriter(destination, fieldnames=list(counts[0]))
            writer.writeheader()
            writer.writerows(counts)
        (args.output_dir / "report.json").write_text(
            json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
    except (OSError, RuntimeError, ValueError) as error:
        logger.error("Unable to inspect CIFAR-10: %s", error)
        logger.info(
            "For the initial download, run: uv run --locked python main.py --download"
        )
        return 1

    logger.info("Saved %s samples to %s", len(labels), args.output_dir)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
