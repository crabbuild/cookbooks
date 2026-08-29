from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


with Path(sys.argv[1]).open(newline="", encoding="utf-8") as handle:
    events = list(csv.DictReader(handle))
destination = Path(sys.argv[2])
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(
    json.dumps(events, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
print(f"snapshotted {len(events)} events")
