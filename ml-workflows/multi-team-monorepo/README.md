# Multi-team monorepo workflows

Three teams own separate workflow files while Crab builds one repository-wide
DAG. Output paths connect `data.prepare` to `train.fit` to `evaluate.score`.
A small root platform stage consumes the shared model without centralizing the
team-owned declarations.

## What it demonstrates

- root-level named `*.workflow.yaml` discovery
- workflow-qualified stage names and cross-file dependency inference
- recursive DAG validation and workflow/stage targeting
- migration from one `crab.lock` to matching split lockfiles
- lockfile conflict resolution after Git merges

## Run the merged DAG

```bash
git init
git add .
git commit -m "add multi-team workflows"

crab config set workflow.discover recursive
crab run --recursive --validate
crab workflow dag --recursive
crab workflow dag --recursive --mermaid
crab workflow dag --recursive --dot
crab run --recursive --json
crab workflow status --json
```

The stage names are `data.prepare`, `train.fit`, `evaluate.score`, and
`catalog`. Select a team's qualified stages or one connected pipeline:

```bash
crab run --stages 'train.*' --dry
crab repro --recursive --pipeline evaluate.score --dry
```

The output-path contract still controls prerequisites: a pipeline target adds
the producers needed for the selected consumer.

## Give each team its own lockfile

Preview and apply the migration:

```bash
crab workflow lockfile split --dry-run
crab workflow lockfile split --keep --update-config
crab run --recursive
git add .crab/config.toml crab.lock *.workflow.lock
git commit -m "split workflow lockfiles by owner"
```

The resulting `data.workflow.lock`, `train.workflow.lock`, and
`evaluate.workflow.lock` can be reviewed with their matching declarations.
`--keep` retains `crab.lock` for the root `crab.yaml` stage in this mixed
single/split layout.

If a Git merge leaves conflict markers in a lockfile, ask Crab to recompute the
safe union and rerun any stage whose two sides disagree:

```bash
crab workflow lockfile resolve --path train.workflow.lock
crab run --recursive
```

`--ours` and `--theirs` are explicit alternatives when repository policy says
one side must win. Prefer the default recomputation for independent changes.
