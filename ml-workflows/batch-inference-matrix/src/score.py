from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    model = json.loads(Path(args.model).read_text(encoding="utf-8"))
    with Path(args.input).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    predictions = []
    for row in rows:
        score = (
            float(model["bias"])
            + float(model["amount_weight"]) * float(row["amount"])
            + float(model["risk_weight"]) * float(row["risk"])
        )
        predictions.append(
            {
                "transaction_id": row["transaction_id"],
                "score": f"{score:.6f}",
                "prediction": int(score >= float(model["threshold"])),
            }
        )
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["transaction_id", "score", "prediction"]
        )
        writer.writeheader()
        writer.writerows(predictions)
    print(f"scored {len(predictions)} rows into {destination}")


if __name__ == "__main__":
    main()
