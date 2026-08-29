from __future__ import annotations

import os
import sys
from pathlib import Path


flag = Path(sys.argv[1]).read_text(encoding="utf-8").strip()
if flag == "fail":
    raise SystemExit("controlled failure requested by control/fail.flag")
destination = Path(sys.argv[2])
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(
    f"region={os.environ.get('MODEL_REGION', 'local')}\n", encoding="utf-8"
)
print(f"wrote {destination}")
