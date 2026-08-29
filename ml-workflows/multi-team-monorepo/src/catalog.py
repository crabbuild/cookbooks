from __future__ import annotations

import json
import sys
from pathlib import Path


model = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
catalog = {"model": "models/model.json", "manifest": model}
destination = Path(sys.argv[2])
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(
    json.dumps(catalog, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
print(f"cataloged {destination}")
