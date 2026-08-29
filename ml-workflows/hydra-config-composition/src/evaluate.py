from __future__ import annotations

import json
import sys
from pathlib import Path


model = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
complexity = model["width"] * model["epochs"]
metrics = {
    "complexity": complexity,
    "quality_proxy": round(1 - model["learning_rate"] - complexity / 10000, 6),
}
destination = Path(sys.argv[2])
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(
    json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
print(json.dumps(metrics, sort_keys=True))
