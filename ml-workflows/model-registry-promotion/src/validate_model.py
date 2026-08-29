from __future__ import annotations

import json
import sys
from pathlib import Path


model = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
weights = model["feature_weights"]
metrics = {
    "feature_count": len(weights),
    "max_abs_weight": max(abs(float(value)) for value in weights.values()),
    "schema_valid": model["format_version"] == 1,
}
destination = Path(sys.argv[2])
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(
    json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
print(json.dumps(metrics, sort_keys=True))
