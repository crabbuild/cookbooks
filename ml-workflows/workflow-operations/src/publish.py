from __future__ import annotations

import sys
from pathlib import Path


mode = sys.argv[1]
receipt = Path(sys.argv[2])
log = Path(sys.argv[3])
receipt.parent.mkdir(parents=True, exist_ok=True)
log.parent.mkdir(parents=True, exist_ok=True)
if mode == "executed":
    receipt.write_text("published\n", encoding="utf-8")
with log.open("a", encoding="utf-8") as handle:
    handle.write(mode + "\n")
print(mode)
