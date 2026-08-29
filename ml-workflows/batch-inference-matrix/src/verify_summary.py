from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> None:
    source = Path(sys.argv[1])
    destination = Path(sys.argv[2])
    metrics = json.loads(source.read_text(encoding="utf-8"))
    report = {
        "accepted": int(metrics["rows"]) == 16,
        "source": source.as_posix(),
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if not report["accepted"]:
        raise SystemExit("expected 16 scored rows")


if __name__ == "__main__":
    main()
