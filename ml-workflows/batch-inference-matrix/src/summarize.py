from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", action="append", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    scores: list[float] = []
    positives = 0
    for source in args.input:
        with Path(source).open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        scores.extend(float(row["score"]) for row in rows)
        positives += sum(int(row["prediction"]) for row in rows)
    metrics = {
        "mean_score": sum(scores) / len(scores),
        "positive_predictions": positives,
        "rows": len(scores),
    }
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(metrics, sort_keys=True))


if __name__ == "__main__":
    main()
