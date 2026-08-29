# Immutable model registry promotion

This cookbook builds and validates a portable JSON churn model, then registers
the exact model bytes as an immutable Crab artifact. Mutable environment labels
point at immutable versions, so deployment automation can promote with
compare-and-swap protection.

## What it demonstrates

- artifact declarations next to the producing workflow
- artifact discovery and manifest inspection
- immutable version creation and retrieval
- staging/production promotion with expected-version CAS
- history inspection and rollback to a prior version

## Build and register a model

```bash
git init
git add .
git commit -m "add model registry example"

crab run --validate
crab run
crab metrics show
git add crab.lock models/churn-model.json metrics/validation.json
git commit -m "record validated model"

crab artifacts list
crab artifacts show churn-model --json
crab artifacts version create churn-model --json
```

Copy the returned immutable version ID into the remaining commands. You can
recover it later from `crab artifacts show churn-model --json`:

```bash
crab artifacts get churn-model --version <version-id> \
  -o downloads/churn-model.json
```

## Promote with compare-and-swap

The first promotion creates the `staging` pointer:

```bash
crab artifacts promote churn-model <version-id> staging
crab artifacts get churn-model --stage staging -o downloads/staging.json
```

After creating a second version, move the pointer only if it still references
the version you reviewed:

```bash
crab artifacts promote churn-model <new-version-id> staging \
  --expected <version-id>
crab artifacts promote churn-model <new-version-id> production
crab artifacts history churn-model --json
```

If another actor changed `staging`, the expected-version check fails instead of
silently overwriting their decision. Rollback is another explicit promotion:

```bash
crab artifacts promote churn-model <version-id> production \
  --expected <new-version-id>
```

Artifact metadata is local until the Git repository and Crab-backed storage are
shared. Configure your own writable remote before using this as a team registry.
