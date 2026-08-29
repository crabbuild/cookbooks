# Hyperparameter experiments and queued sweeps

This two-stage classifier makes experiment state easy to inspect. The training
parameters live in `params.json`; every experiment records the parameter diff,
generated model, and evaluation metrics without changing the main workspace.

## What it demonstrates

- named `crab exp run` experiments with parameter overrides
- experiment listing, inspection, comparison, rename, save, apply, and reset
- selecting a result with `exp promote`
- queued Cartesian sweeps and worker lifecycle commands
- experiment cleanup, garbage collection, and remote synchronization
- `crab params` and `crab metrics` evidence commands

## Establish the baseline

```bash
git init
git add .
git commit -m "add hyperparameter sweep"

crab run --validate
crab run --json
git add crab.lock models/model.json metrics/evaluation.json
git commit -m "record baseline model"

crab params show
crab metrics show
crab exp save -n baseline
```

## Compare named experiments

```bash
crab exp run -n fast \
  -S train.learning_rate=0.3 \
  -S train.l2=0.02
crab exp run -n conservative \
  -S train.learning_rate=0.1 \
  -S train.l2=0.1

crab exp ls
crab exp show <fast-id> --json
crab exp diff <fast-id> <conservative-id>
crab exp rename <fast-id> high-rate
```

`crab exp ls` displays the immutable IDs beside their human-readable names.
Commands that inspect or mutate one experiment accept an ID or unambiguous ID
prefix. To compare an applied result with the baseline:

```bash
crab exp apply <fast-id>
crab params diff HEAD
crab metrics diff HEAD
```

Apply copies that experiment's state into the current workspace, so use a clean
disposable branch and restore it with your normal Git workflow after review.
`crab exp reset <experiment-id>` resets that experiment's checkpoint lineage;
it does not undo a workspace apply. `crab exp promote <experiment-id>` creates
a Git branch for a selected result.

## Run a queued grid search

Queue a 3 x 3 grid and let two workers consume it:

```bash
crab exp queue -S 'train.learning_rate=0.05,0.15,0.3' \
  -S 'train.l2=0.0,0.01,0.1'
crab queue start --jobs 2
crab queue status
crab queue logs <task-id>
crab queue stop
```

The same worker controls are available below the experiment namespace:
`crab exp start`, `crab exp status`, and `crab exp stop`. For an individual
task, use `crab queue logs <task-id>`, `crab queue kill <task-id>`, or
`crab queue remove <task-id>`. `crab exp remove <experiment-id>`,
`crab exp clean`, and
`crab exp gc` reclaim experiment state.

Preview destructive cleanup before applying it:

```bash
crab exp remove <experiment-id> --dry-run
crab exp gc --keep 20 --dry-run --json
crab exp clean --json
```

## Share experiments

These commands are **remote required**:

```bash
crab exp push <experiment-id>
crab exp pull <experiment-id>
```

Configure a writable Crab Git remote before running them. The repository never
embeds a token or organization-specific remote.
