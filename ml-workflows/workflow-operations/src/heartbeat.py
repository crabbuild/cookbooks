from __future__ import annotations

import json
import sys
import time
from pathlib import Path


destination = Path(sys.argv[1])
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(
    json.dumps({"generated_at_unix_ns": time.time_ns()}, indent=2) + "\n",
    encoding="utf-8",
)
print(f"refreshed {destination}")
