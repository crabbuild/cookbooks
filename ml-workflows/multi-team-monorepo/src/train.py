from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


with Path(sys.argv[1]).open(newline="", encoding="utf-8") as handle:
    values = [float(row["engagement"]) for row in csv.DictReader(handle)]
model = {"threshold": round(sum(values) / len(values), 6), "version": 1}
destination = Path(sys.argv[2])
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(
    json.dumps(model, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
print(json.dumps(model, sort_keys=True))
