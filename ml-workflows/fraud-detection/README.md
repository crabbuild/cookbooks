# Crab ML fraud-detection example

This dependency-free Python 3 example exercises a four-stage Crab workflow:

```text
transactions.csv -> raw.csv -> features.csv -> fraud-model.pkl -> metrics + plot
```

Run it from this directory with the `crab` CLI installed:

```bash
crab run --validate
crab workflow dag
crab run --parallelism 2 --json
crab workflow status --json
crab params show --json
crab metrics show
crab metrics plot --format vega -o validation/precision-recall.vega.json
crab plots show --json
crab plots templates --json
python3 src/smoke_model.py
python3 src/check_quality_gate.py
crab run --parallelism 2 --json
```

The final run should report a cache hit for all four stages. No Python packages
outside the standard library are required. A Crab remote is optional for these
local commands; configure one before using remote cache, experiment sharing, or
clean-client examples from the accompanying guides.

After committing a baseline run, compare its plot data with workspace changes:

```bash
git add crab.lock data/raw.csv data/features.csv models/fraud-model.pkl \
  metrics/evaluation.json plots/precision_recall.csv
git commit -m "record fraud model baseline"
crab plots diff HEAD --format vega -o validation/plot-diff.vega.json
```

The model uses Python pickle to match the artifact examples. Load pickle files
only when their source and content identity are trusted.

Read the full walkthrough in the
[Crab ML workflow library](https://crab.build/library/ml-fraud-detection-workflow).
