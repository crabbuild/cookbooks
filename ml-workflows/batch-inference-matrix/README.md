# Batch inference with `foreach` and `matrix`

This cookbook scores two regional transaction batches with two model policies.
It expands two normalization stages and four scoring stages from compact YAML,
then aggregates every prediction into one metrics record.

```text
data/{north,south}.csv
  -> normalize@{north,south}
  -> score@{north,south}-{linear,robust}
  -> summarize
```

## What it demonstrates

- `${...}` workflow templating from `vars`
- dictionary-form `foreach` and Cartesian `matrix` expansion
- portable `cmd.argv` execution without shell syntax
- inferred edges between expanded producers and consumers
- stage targeting with `--stages`, `--glob`, `--pipeline`, and `--single-item`
- freeze/unfreeze policy
- inline cached stages and persistent authoring with `crab stage add`

## Run the expanded DAG

```bash
git init
git add .
git commit -m "add batch inference matrix"

crab run --validate
crab workflow dag
crab stage list --json
crab run --parallelism 4 --json
crab metrics show
```

The DAG contains seven expanded/explicit stages: two normalizers, four scorers,
and one summary. `metrics/summary.json` reports 16 scored rows.

Run only matching score stages and their prerequisites:

```bash
crab run --stages "score@north-*" --dry --explain-miss
crab repro --glob "score@north-*"
crab repro --pipeline "score@north-linear" --dry
crab repro --single-item "score@north-linear" --dry
crab repro --downstream "normalize@north" --dry
crab repro --all-pipelines --dry
```

`--single-item` does not add missing producers. Use it only when the selected
stage's declared inputs already exist.

## Freeze shared preprocessing

```bash
crab freeze "normalize@north" "normalize@south" --json
crab run --dry
crab unfreeze "normalize@north" "normalize@south" --json
```

Freeze edits `crab.yaml`. Review or restore that declaration before committing.

## Run one inline cached check

```bash
crab run --name inspect-summary \
  --deps metrics/summary.json \
  --deps src/verify_summary.py \
  --outs reports/inspection.json \
  -- python3 src/verify_summary.py metrics/summary.json reports/inspection.json
```

Persist a similar stage in `crab.yaml`:

```bash
crab stage add -n inspect_summary \
  -d metrics/summary.json \
  -d src/verify_summary.py \
  -o reports/stage-inspection.json \
  --run \
  python3 src/verify_summary.py metrics/summary.json reports/stage-inspection.json
crab stage list
```

The authoring command intentionally changes the workflow declaration. Run it in
a disposable branch when you only want to explore the CLI.
