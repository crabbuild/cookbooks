from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_scalar_yaml(path: Path) -> dict[str, object]:
    root: dict[str, object] = {}
    stack: list[tuple[int, dict[str, object]]] = [(-1, root)]
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip())
        key, separator, raw_value = raw_line.strip().partition(":")
        if not separator:
            raise ValueError(f"unsupported YAML line: {raw_line}")
        while stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        value = raw_value.strip()
        if not value:
            child: dict[str, object] = {}
            parent[key] = child
            stack.append((indent, child))
            continue
        try:
            parent[key] = json.loads(value)
        except json.JSONDecodeError:
            parent[key] = value
    return root


parser = argparse.ArgumentParser()
parser.add_argument("--params", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()
params = parse_scalar_yaml(Path(args.params))["train"]
if not isinstance(params, dict):
    raise ValueError("train config must be a mapping")
model_config = params["model"]
optimizer_config = params["optimizer"]
if not isinstance(model_config, dict) or not isinstance(optimizer_config, dict):
    raise ValueError("model and optimizer configs must be mappings")
model = {
    "epochs": int(params["epochs"]),
    "family": str(model_config["name"]),
    "learning_rate": float(optimizer_config["learning_rate"]),
    "optimizer": str(optimizer_config["name"]),
    "width": int(model_config["width"]),
}
destination = Path(args.output)
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(
    json.dumps(model, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
print(json.dumps(model, sort_keys=True))
