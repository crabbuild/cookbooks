from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--params", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    params = json.loads(Path(args.params).read_text(encoding="utf-8"))["train"]
    with Path(args.data).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    positive_rate = sum(int(row["label"]) for row in rows) / len(rows)
    learning_rate = float(params["learning_rate"])
    l2 = float(params["l2"])
    epochs = int(params["epochs"])
    model = {
        "bias": round(positive_rate - l2, 6),
        "epochs": epochs,
        "learning_rate": learning_rate,
        "threshold": round(0.5 + abs(learning_rate - 0.15) + l2, 6),
    }
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(model, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(model, sort_keys=True))


if __name__ == "__main__":
    main()
