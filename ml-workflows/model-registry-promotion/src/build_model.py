from __future__ import annotations

import json
import sys
from pathlib import Path


source = Path(sys.argv[1])
destination = Path(sys.argv[2])
spec = json.loads(source.read_text(encoding="utf-8"))
model = {**spec, "format_version": 1, "training_revision": "cookbook-v1"}
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(
    json.dumps(model, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
print(f"built {destination}")
