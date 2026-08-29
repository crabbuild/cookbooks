from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with Path(args.input).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    normalized = [
        {
            "transaction_id": row["transaction_id"],
            "amount": f"{float(row['amount']):.2f}",
            "risk": f"{float(row['risk']):.4f}",
        }
        for row in rows
    ]
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["transaction_id", "amount", "risk"]
        )
        writer.writeheader()
        writer.writerows(normalized)
    print(f"normalized {len(normalized)} rows into {destination}")


if __name__ == "__main__":
    main()
