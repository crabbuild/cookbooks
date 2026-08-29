# Weekly card-not-present fraud detection

This dependency-free Python 3 cookbook models a payments team retraining a
fraud classifier every week. Crab records which transaction snapshot,
parameters, source files, and stage outputs produced the model, metrics, and
precision-recall curve.

```text
data/transactions.csv
  -> ingest -> data/raw.csv
  -> features -> data/features.csv
  -> train -> models/fraud-model.pkl
  -> evaluate -> metrics/evaluation.json + plots/precision_recall.csv
```

The input is deliberately small enough to inspect, but the dependency and
cache boundaries are the same ones used when the dataset and model live in
object storage.

## What it demonstrates

- a four-stage producer-to-consumer DAG
- source, dataset, parameter, model, metric, and plot dependencies
- content-addressed stage reuse and downstream invalidation
- flattened parameter and metric inspection
- Vega-Lite plot rendering and revision comparison
- a declared model artifact ready for immutable versioning
- a model smoke test and a recall quality gate

## Prerequisites

- Crab 1.1.0 or newer on `PATH`
- Python 3.10 or newer
- Git

Every training and validation script uses only the Python standard library.

## Run the workflow

Each cookbook folder is an independent repository example. Initialize and
commit the inputs before the first run so Crab has a reproducible Git boundary:

```bash
git init
git add .
git commit -m "add fraud detection workflow"

crab run --validate
crab workflow dag
crab run --parallelism 2 --json
```

Validation checks the declaration without executing a command. The run then
creates these outputs:

```text
crab.lock
data/raw.csv
data/features.csv
models/fraud-model.pkl
metrics/evaluation.json
plots/precision_recall.csv
```

The example starts with 17 transactions. The 30-day feature window removes one
old row, leaving 10 training rows and 6 test rows. With the committed parameters,
the expected test metrics are:

```json
{
  "accuracy": 1.0,
  "f1": 1.0,
  "precision": 1.0,
  "recall": 1.0,
  "samples": 6,
  "threshold": 0.5
}
```

These values prove the cookbook ran as expected; they are not a production
quality claim for a 17-row dataset.

## Understand the stage boundaries

| Stage | Inputs that affect its key | Result |
| --- | --- | --- |
| `ingest` | raw transactions and ingest/common source | normalized, sorted transaction snapshot |
| `features` | normalized data, feature source, `features.lookback_days` | four model features plus labels and split |
| `train` | features, training source, all `train.*` values | seeded logistic-regression model |
| `evaluate` | model, features, evaluation source, threshold and recall floor | scalar metrics and precision-recall data |

Crab infers the edges because one stage's output path appears in a consumer's
dependencies. A change to `train.learning_rate` reruns `train` and `evaluate`
without repeating ingestion or feature engineering. A transaction change
invalidates all four stages.

Inspect the current evidence and ask why a stage is stale:

```bash
crab workflow status --json
crab workflow status --why train
crab params show --json
crab metrics show
```

## Prove cache reuse

Run the same committed inputs again:

```bash
crab run --parallelism 2 --json
```

All four stage results should report `cache_hit: true`. Crab verifies the
command, declared dependencies, selected parameters, and environment before
materializing a cached result.

Preview invalidation without executing after editing data, source, or
`params.json`:

```bash
crab run --dry --explain-miss
crab repro train --downstream --dry
```

The dry run shows which input hash changed and which consumers would follow it.

## Inspect model quality and plots

The smoke test checks the serialized model schema. The quality gate exits
non-zero when recall is below the requested floor:

```bash
python3 src/smoke_model.py
python3 src/check_quality_gate.py
python3 src/check_quality_gate.py --minimum-recall 0.90
```

Render the declared precision-recall data as a table or Vega-Lite document:

```bash
crab plots show
crab metrics plot --format vega \
  -o validation/precision-recall.vega.json
crab plots templates --json
```

Commit a successful baseline before comparing it with later workspace results:

```bash
git add crab.lock data/raw.csv data/features.csv models/fraud-model.pkl \
  metrics/evaluation.json plots/precision_recall.csv
git commit -m "record fraud model baseline"

crab params diff HEAD
crab metrics diff HEAD
crab plots diff HEAD --format vega \
  -o validation/plot-diff.vega.json
```

With no workspace change the diffs are empty or identical. Edit a declared
parameter and rerun to see the parameter, scalar metric, and curve evidence
together.

## Register the model as an immutable artifact

`crab.yaml` declares `models/fraud-model.pkl` as the `fraud-model` artifact.
After committing the clean model output:

```bash
crab artifacts list
crab artifacts show fraud-model --json
crab artifacts version create fraud-model --json
```

The returned content-addressed version can be retrieved or promoted without
changing its bytes. Continue with the
[model registry promotion cookbook](../model-registry-promotion/README.md) for
retrieval, compare-and-swap environment labels, history, and rollback.

## Use a remote cache in CI

All commands above work locally. Publishing stage results, sharing experiments,
or proving cache-only replay in a clean clone requires a writable Crab remote.
The [remote cache CI cookbook](../remote-cache-ci/README.md) covers that trust
boundary without embedding credentials or an organization-specific URL.

## Safety and troubleshooting

- The model uses Python pickle to demonstrate a realistic binary artifact.
  Load pickle files only when the source and content identity are trusted.
- If validation fails, fix `crab.yaml` before running; validation executes no
  stage commands.
- If the quality gate fails, inspect `metrics/evaluation.json`, the threshold,
  and the precision-recall plot before changing the recall floor.
- If a result reruns unexpectedly, use `crab workflow status --why <stage>` or
  `crab run --dry --explain-miss` instead of forcing cache reuse.

For the article-length walkthrough, see the
[Crab ML workflow library](https://crab.build/library/ml-fraud-detection-workflow).
