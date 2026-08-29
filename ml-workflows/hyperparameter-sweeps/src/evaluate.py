from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    model = json.loads(Path(args.model).read_text(encoding="utf-8"))
    with Path(args.data).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    predictions = [
        int(float(row["feature"]) + model["bias"] >= model["threshold"])
        for row in rows
    ]
    labels = [int(row["label"]) for row in rows]
    accuracy = sum(a == b for a, b in zip(predictions, labels, strict=True)) / len(rows)
    score = accuracy - abs(model["learning_rate"] - 0.15) - model["threshold"] / 100
    metrics = {"accuracy": accuracy, "selection_score": round(score, 6)}
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(metrics, sort_keys=True))


if __name__ == "__main__":
    main()
