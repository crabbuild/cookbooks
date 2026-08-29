# Operating a workflow under change and failure

This DAG has a controlled failure branch, an unrelated branch, an optional
report, a nondeterministic heartbeat, and a publish-like side effect. It is a
safe local lab for the operational flags that are difficult to demonstrate in
a happy-path training pipeline.

## What it demonstrates

- `--keep-going` and `--ignore-errors` partial-success policies
- conditions, declared environment hashing, timeout, and nondeterminism
- cache-hit hooks for stages with external side effects
- status explanations, journals, scheduler lock controls, and recovery flags
- watch and interactive execution modes

## Run the healthy path twice

```bash
git init
git add .
git commit -m "add workflow operations lab"

ENABLE_REPORT=1 MODEL_REGION=us crab run --validate
ENABLE_REPORT=1 MODEL_REGION=us crab run --json
ENABLE_REPORT=1 MODEL_REGION=us crab run --json
```

`heartbeat` executes every time because it is explicitly nondeterministic.
`publish_receipt` reuses its cached output on the second run and invokes its
`on_cache_hit` hook; `status/publish-events.log` records both paths. Remove
`ENABLE_REPORT` and the optional stage is skipped by its condition.

Changing a declared environment value changes the `risky_transform` stage key:

```bash
MODEL_REGION=eu crab run risky_transform --dry --explain-miss
crab workflow status --why risky_transform
```

Inline mode can combine an empty environment, a timeout, and Crab's hermetic
sandbox. This system-binary probe is portable on macOS and Linux runners:

```bash
crab run --name hermetic-probe \
  --outs output/hermetic.ok \
  --empty-env \
  --timeout 10s \
  --hermetic \
  -- /usr/bin/touch output/hermetic.ok
```

## Exercise partial failure

Switch the tracked control input to `fail`, force execution, and inspect the
result. These runs intentionally return a non-zero exit status:

```bash
python3 -c 'from pathlib import Path; Path("control/fail.flag").write_text("fail\n")'
crab run --force --keep-going --json
crab run --force --ignore-errors --json
crab workflow status --json
```

With `--keep-going`, `dependent_report` does not start after its producer fails,
but the unrelated `independent_report` can finish. `--ignore-errors` attempts
every remaining stage; a missing producer output still surfaces as an error.
Restore the healthy input before continuing:

```bash
python3 -c 'from pathlib import Path; Path("control/fail.flag").write_text("pass\n")'
crab run
```

## Inspect journals and scheduler state

```bash
crab workflow journal ls --json
crab workflow journal show <run-id> --json
crab workflow journal gc --keep 10 --dry-run --json
crab workflow dag --json
crab run --no-wait --dry
crab run --lock-timeout 30 --dry
```

Use `crab run --interactive` for an operator-confirmed run and `crab run
--watch` during local development. Both wait for user input or filesystem
events, so they are deliberately not part of unattended verification.

`--resume-trust-outputs` and `--abandon <run-id>` are recovery controls for a
genuinely interrupted journal. Inspect `workflow journal show` first: trusting
unrecorded outputs or abandoning the wrong active run discards useful proof.
