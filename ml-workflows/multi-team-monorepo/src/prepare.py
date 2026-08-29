from __future__ import annotations

import csv
import sys
from pathlib import Path


with Path(sys.argv[1]).open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
destination = Path(sys.argv[2])
destination.parent.mkdir(parents=True, exist_ok=True)
with destination.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=["account_id", "engagement"])
    writer.writeheader()
    for row in rows:
        engagement = int(row["events"]) + float(row["spend"]) / 100
        writer.writerow({"account_id": row["account_id"], "engagement": f"{engagement:.4f}"})
print(f"prepared {len(rows)} accounts")
