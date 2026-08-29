from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


with Path(sys.argv[1]).open(newline="", encoding="utf-8") as handle:
    values = [float(row["engagement"]) for row in csv.DictReader(handle)]
model = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
positive_rate = sum(value >= model["threshold"] for value in values) / len(values)
metrics = {"accounts": len(values), "positive_rate": positive_rate}
destination = Path(sys.argv[3])
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(
    json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
print(json.dumps(metrics, sort_keys=True))
