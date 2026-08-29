# ML workflow cookbooks

Each folder is an independent Git repository example. Copy one folder, run
`git init`, commit its inputs, and follow its README. Every Python example uses
only the standard library.

| Cookbook | Primary capability |
| --- | --- |
| [Fraud detection](fraud-detection/README.md) | End-to-end DAG, params, metrics, plots, cache reuse |
| [Batch inference matrix](batch-inference-matrix/README.md) | Templating, `foreach`, `matrix`, targeting, stage authoring |
| [Hyperparameter sweeps](hyperparameter-sweeps/README.md) | Experiments, diffs, queues, workers, result selection |
| [Remote cache CI](remote-cache-ci/README.md) | Cache controls, publication, clean-runner replay |
| [Model registry promotion](model-registry-promotion/README.md) | Immutable artifacts, labels, CAS promotion, rollback |
| [Multi-team monorepo](multi-team-monorepo/README.md) | Multiple workflow files, recursive DAGs, split lockfiles |
| [Workflow operations](workflow-operations/README.md) | Partial failure, conditions, side effects, journals, locks |
| [Hydra config composition](hydra-config-composition/README.md) | Config groups, composed params, experiment overrides |

## Public command coverage

| Command family or behavior | Cookbook |
| --- | --- |
| `crab run`, `crab repro`, target modes, JSON/JSONL | Fraud detection, batch inference, remote cache CI |
| Inline stages, `crab stage add/list` | Batch inference matrix |
| `crab freeze` / `crab unfreeze` | Batch inference matrix |
| Validation, status, DAG formats | Every declarative workflow |
| Journals, locks, failure continuation, conditions | Workflow operations |
| Local and remote stage cache controls | Remote cache CI |
| `crab exp` lifecycle | Hyperparameter sweeps, Hydra composition |
| `crab queue` task operations | Hyperparameter sweeps |
| `crab params`, `crab metrics`, `crab plots` | Fraud detection, hyperparameter sweeps |
| `crab artifacts` lifecycle | Model registry promotion |
| Recursive discovery and split lockfiles | Multi-team monorepo |
| Templating, `foreach`, `matrix`, argv commands | Batch inference matrix |
| Hydra config groups | Hydra config composition |
| Watch, interactive, timeout, environment hashing | Workflow operations |

Commands that publish cache entries, experiments, or artifacts to a remote are
marked **remote required**. Substitute a writable `crab://` repository owned by
your organization; no cookbook contains credentials or a live remote name.

`crab workflow checkpoint` is not included. It is a hidden stage-to-supervisor
protocol, and Crab's release documentation currently marks clean-clone
checkpoint qualification incomplete.
