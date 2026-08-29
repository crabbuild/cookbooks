# Hydra-style configuration composition

This cookbook separates model and optimizer choices into reusable config
groups. Crab composes those files into `params.yaml` inside each experiment
worktree, then the same declared DAG trains and evaluates the selected setup.
The trainer reads that composed file directly, and the stage declares every
consumed key so cache invalidation remains precise.

## What it demonstrates

- committed Hydra config roots and defaults
- model and optimizer config groups
- config-group selection plus dotted scalar overrides
- composed parameter participation in stage commands and cache keys
- experiment evidence for the resolved configuration

## Run the committed baseline

```bash
git init
git add .
git commit -m "add Hydra composition example"

crab run --validate
crab run
crab params show
crab metrics show
git add crab.lock models/model.json metrics/evaluation.json
git commit -m "record composed baseline"
```

The committed `params.yaml` mirrors the default `linear` + `adam` composition,
so regular workflow runs and experiments share the same baseline contract.

## Select config groups in experiments

```bash
crab exp run -n tree-sgd \
  -S train/model=tree \
  -S train/optimizer=sgd

crab exp run -n tree-low-rate \
  -S train/model=tree \
  -S train/optimizer=sgd \
  -S train.optimizer.learning_rate=0.02

crab exp ls
crab exp show <tree-low-rate-id> --json
crab exp diff <tree-sgd-id> <tree-low-rate-id>
```

Group overrides such as `train/model=tree` select a YAML file. Dotted
overrides such as `train.optimizer.learning_rate=0.02` change a scalar after
group composition, so the dotted value wins.

`exp ls` shows immutable experiment IDs beside the friendly names. `exp diff`
includes both parameter and metric changes between those experiment records.

Use `crab exp run -S train/model=tree --dry --json` to inspect a plan without
executing commands. If composition fails in another clone, verify that `conf/`,
`params.yaml`, and `.crab/config.toml` are all committed; never put credentials
or machine-specific paths in those files.
