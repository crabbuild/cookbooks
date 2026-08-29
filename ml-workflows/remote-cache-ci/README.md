# Remote stage cache in CI

This cookbook turns raw product events into a committed snapshot and a user
feature table. The computation is intentionally small; the workflow shows the
same cache publication and replay boundary used by expensive GPU or Spark jobs.

## What it demonstrates

- validation, dry runs, cache-miss explanations, JSONL event output
- named workflow selection with inferred cross-workflow dependencies
- normal reuse, force controls, and run-cache policy
- explicit cache publication and clean-runner cache-only replay
- strict and permissive missing-cache behavior
- output pulling and validation without command execution

## Prove local reuse first

```bash
git init
git add .
git commit -m "add remote cache CI example"

crab run --validate
crab run --dry --explain-miss
crab run --jsonl | tee workflow-events.jsonl
crab run --json
crab run --workflow features --dry
```

The second run reuses both stages. Compare the available recomputation controls
before putting them into automation:

```bash
crab run --force --dry
crab run --force-downstream snapshot --dry
crab run --no-run-cache --dry
crab run --no-commit --dry
crab run --no-overwrite --dry
```

`--force` and `--force-downstream` deliberately bypass valid results.
`--no-run-cache` disables local cache reuse for that invocation. `--no-commit`
does not update the lockfile, while `--no-overwrite` protects existing outputs.

## Publish from a trusted runner

The following section is **remote required**. Initialize this copied example
with a writable Crab URL controlled by your team, then run:

```bash
crab run --cache-push --jsonl
crab workflow push-cache --all --json
crab workflow status --cloud --json
git add crab.lock
git commit -m "record reproducible feature workflow"
git push origin HEAD
```

`--cache-push` publishes results produced by the run. `workflow push-cache
--all` publishes every local cache entry missing from the configured remote,
and cloud status compares the local stage cache with that remote.

## Prove a clean CI runner cannot recompute

In a fresh clone with the same Crab remote configured:

```bash
crab run --pull --cache-only --jsonl
crab run --pull --validate
```

`--cache-only` fails if any required stage result is absent, which makes it a
strong release gate. `--allow-missing` is the deliberate permissive alternative
for a missing local dependency whose unchanged digest is already in the
committed lockfile:

```bash
crab run --pull --cache-only --allow-missing --json
```

Do not use the permissive form when the clean runner is meant to prove that
every declared input and cache entry is available.
