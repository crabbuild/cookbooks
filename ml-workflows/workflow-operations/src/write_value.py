from __future__ import annotations

import sys
from pathlib import Path


destination = Path(sys.argv[2])
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(sys.argv[1] + "\n", encoding="utf-8")
print(f"wrote {destination}")
