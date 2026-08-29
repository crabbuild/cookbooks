from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path


events = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
features: dict[str, dict[str, float | int]] = defaultdict(
    lambda: {"event_count": 0, "total_amount": 0.0}
)
for event in events:
    user = features[event["user_id"]]
    user["event_count"] += 1
    user["total_amount"] = round(float(user["total_amount"]) + float(event["amount"]), 2)
destination = Path(sys.argv[2])
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(
    json.dumps(dict(sorted(features.items())), indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
print(f"materialized features for {len(features)} users")
