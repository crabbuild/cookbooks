# Manage Git LFS with Crab and RustFS

> **Verified locally — 2026-08-29.** This command-only cookbook was written
> after a fresh Crab 1.1.0 qualification against RustFS
> <code>rustfs/rustfs:1.0.0-beta.8-glibc</code>. The disposable run uploaded
> four deterministic 1 MiB objects, cloned the Git history, fetched the
> objects, checked out the bytes, and proved SHA-256 identity. No credential or
> generated evidence is stored in this folder.

This is a practical guide for a model-release repository whose source stays in
Git while large model files use standard Git LFS pointers. Crab runs the LFS
filters and transfer agent locally and writes the LFS objects directly to your
S3, GCS, Azure, or S3-compatible bucket. There is no Crab data server and no
Git LFS HTTP gateway to deploy.

The cookbook uses shell, Git, and Crab commands only. It does not require a
Python data-generation script.

## The repository you will build

The scenario is a team publishing model checkpoints and occasionally locking a
release while a validation job runs:

~~~text
fraud-model/
├── .crab.toml                    # Crab remote; safe to commit
├── .gitattributes                # committed representation boundary
├── models/releases/model-v1.bin  # standard Git LFS pointer in Git
├── src/                          # ordinary Git source
└── validation/                   # ordinary Git reports

Git commit + LFS pointer ── Crab remote helper ──┐
                                                  ├─ object storage
LFS bytes ───── crab transfer agent ─────────────┘
~~~

An LFS object is stored below the repository prefix as
<code>lfs/objects/&lt;first-two&gt;/&lt;next-two&gt;/&lt;sha256&gt;</code>. Git stores only
the small pointer blob. Keep credentials in your normal cloud credential chain
or environment; never put them in <code>.crab.toml</code> or this cookbook.

## Choose LFS or native Crab per path

The matching <code>.gitattributes</code> rule, not file size or extension,
chooses the representation. LFS and Crab-native files can coexist:

~~~gitattributes
models/releases/** filter=lfs  diff=lfs  merge=lfs  -text lockable
datasets/**         filter=crab diff=crab merge=crab -text
~~~

Use <code>crab lfs track</code> for existing LFS tooling, standard Git LFS
pointers, and whole-file object semantics. Use <code>crab track</code> for new
Crab/Xet paths that benefit from chunk-level deduplication. Do not add both
filters to the same path.

## Prerequisites and environment

- Crab 1.1.0 or newer on <code>PATH</code> (<code>crab version</code>). Install
  Crab normally so the <code>git-remote-crab</code> helper is also discoverable
  by Git.
- Git. Git LFS is optional when every transfer uses <code>crab lfs</code>; it is
  useful for existing tools and for testing standard <code>git lfs</code>
  commands through Crab's custom transfer agent.
- A writable bucket/prefix and credentials with read/write access to that
  prefix. For S3-compatible storage, set the endpoint and path-style options
  required by that service.

For a disposable local RustFS run, keep these values in your shell session
only (use your own bucket and credentials):

~~~bash
export AWS_ACCESS_KEY_ID="<local-rustfs-access-key>"
export AWS_SECRET_ACCESS_KEY="<local-rustfs-secret-key>"
export AWS_REGION="us-east-1"
export AWS_ENDPOINT_URL="http://127.0.0.1:19000"
export AWS_ALLOW_HTTP=true
export CRAB_S3_FORCE_PATH_STYLE=true
export CRAB_LFS_REMOTE="crab://crab-lfs-cookbook/model-release"
~~~

Create the bucket with the RustFS-compatible S3 API before <code>crab init</code>:

~~~bash
aws --endpoint-url "$AWS_ENDPOINT_URL" s3api create-bucket --bucket crab-lfs-cookbook
~~~

Do not copy placeholder credentials or the disposable bucket name into a
production repository.

## 1. Initialize the Crab remote and LFS integration

From a new repository:

~~~bash
mkdir fraud-model
cd fraud-model
git init --initial-branch=main
git config user.name "Model Platform"
git config user.email "model-platform@example.invalid"

crab init --storage-provider s3 "$CRAB_LFS_REMOTE"
crab lfs install --local

git remote -v
git config --local --get lfs.standalonetransferagent
crab lfs env
~~~

<code>crab init</code> writes the repository's Crab remote configuration and
creates the normal <code>origin</code> Git remote. <code>crab lfs
install --local</code> writes local Git config for:

1. <code>filter=lfs</code> clean and smudge conversion;
2. the <code>crab</code> standalone transfer agent used by an unmodified
   <code>git-lfs</code>; and
3. the pre-push gate that uploads LFS objects before the Git ref is published.

The filter and hook configuration lives in <code>.git/config</code> and
<code>.git/hooks</code>. Commit <code>.crab.toml</code> and
<code>.gitattributes</code>, never those private files or a credential. If an
unmanaged pre-push hook already exists, installation stops so an upload gate
cannot be silently lost. Merge the printed command manually, or use
<code>--force</code> only when replacing that hook is intentional:

~~~bash
crab lfs install --local --force
crab lfs update
~~~

To inspect the commands without changing Git config, use manual mode. To
remove the local integration later, uninstall only the repository-scoped
configuration:

~~~bash
crab lfs install --local --manual
crab lfs uninstall --local
~~~

For CI that should keep pointers in the worktree, use
<code>crab lfs install --local --skip-smudge</code>. Install the repository hook
unless a separate CI step is responsible for calling
<code>crab lfs push</code>.

## 2. Track model files and inspect the pointer boundary

Create the directory, preview the rule, then write it:

~~~bash
mkdir -p models/releases src validation
crab lfs track --dry-run --lockable 'models/releases/**'
crab lfs track --lockable 'models/releases/**'
cat .gitattributes
~~~

The rule is ordinary text and must be committed. Add a representative binary
without a helper script; <code>head</code> is available on macOS and Linux:

~~~bash
head -c 2097152 /dev/zero > models/releases/model-v1.bin
git add .crab.toml .gitattributes models/releases/model-v1.bin
~~~

The index should contain a small standard Git LFS pointer, while the full bytes
are in the local LFS cache:

~~~bash
git cat-file -s :models/releases/model-v1.bin
git cat-file -p :models/releases/model-v1.bin

crab lfs pointer --file models/releases/model-v1.bin
crab lfs pointer --file models/releases/model-v1.bin > /tmp/model-v1.pointer
crab lfs pointer --stdin --check --strict < /tmp/model-v1.pointer
crab lfs ls-files --long --size --json
crab lfs status --json
~~~

The pointer contains <code>version</code>, a SHA-256 <code>oid</code>, and the
byte <code>size</code>. The pointer check validates the exact canonical format;
it does not download an object.

Commit the boundary and the first model:

~~~bash
git commit -m "track model releases with Crab LFS"
~~~

To remove a rule later, preview first, then untrack and commit the resulting
<code>.gitattributes</code> change:

~~~bash
crab lfs track --dry-run --not-lockable 'models/releases/**'
crab lfs untrack 'models/releases/**'
git add .gitattributes
git commit -m "stop tracking model releases with LFS"
~~~

<code>untrack</code> changes attributes; it does not rewrite old commits or
delete objects already in the bucket.

## 3. Publish safely

The normal Git loop is enough when the Crab pre-push hook is installed:

~~~bash
crab lfs status --porcelain
git push origin main
~~~

On a brand-new `crab://` prefix, use that normal `git push` once before calling
the standalone LFS uploader. The first push creates the Crab Git layout while
the pre-push hook uploads the object. Calling `crab lfs push` against an
uninitialized prefix can leave bytes present without a publishable Git layout.

For an explicit and auditable LFS boundary, preview and upload the objects
after the remote has been initialized:

~~~bash
crab lfs push origin main --dry-run
crab lfs push origin main
git push origin main
~~~

<code>crab lfs push</code> accepts refs, object IDs, all local objects, or stdin:

~~~bash
crab lfs push origin main --all --dry-run
crab lfs push origin --object-id OID_HEX --dry-run
printf 'main\n' | crab lfs push origin --stdin --dry-run
~~~

The fetch side has matching selection and replay controls. JSON output cannot
be combined with fetch-time pruning:

~~~bash
printf 'main\n' | crab lfs fetch origin --stdin
crab lfs fetch origin --recent
crab lfs fetch origin main --refetch --dry-run --json
crab lfs fetch origin main --prune
~~~

The ref push is deliberately last. If an LFS object is missing or corrupt,
Crab fails before making the Git ref visible. The same object path is usable by
an unmodified Git LFS client after <code>crab lfs install</code>:

~~~bash
git lfs push origin main
~~~

## 4. Clone and retrieve only what you need

For a large repository, clone history without expanding LFS pointers:

~~~bash
GIT_LFS_SKIP_SMUDGE=1 git clone "$CRAB_LFS_REMOTE" fraud-model-client
cd fraud-model-client
crab lfs install --local --skip-smudge
~~~

If you intentionally do not want Crab to install repository hooks in this
clone, add <code>--skip-repo</code>; this also means pushes will not be gated by
the Crab hook.

Inspect the pointer inventory without downloading model bytes:

~~~bash
crab lfs ls-files --name-only
crab lfs ls-files --long --size --json
crab lfs status --porcelain
~~~

Fetch a subset, then materialize only matching paths:

~~~bash
crab lfs fetch origin main --include 'models/releases/**' --json
crab lfs checkout 'models/releases/**'
~~~

Fetch all referenced objects when local disk permits it:

~~~bash
crab lfs fetch origin main --all
crab lfs checkout
~~~

<code>fetch</code> populates <code>.git/lfs/objects</code>; <code>checkout</code>
replaces matching pointer files with verified bytes from that cache.
<code>pull</code> combines those two actions:

~~~bash
crab lfs pull origin
crab lfs pull origin --include 'models/releases/**'
crab lfs pull origin --exclude 'models/releases/archived/**'
~~~

With Git LFS installed, <code>git lfs fetch</code>, <code>git lfs checkout</code>,
and <code>git lfs pull</code> use the same Crab standalone transfer agent.
<code>crab lfs clone</code> is a deprecated compatibility wrapper around clone
plus Crab LFS transfer; prefer the explicit
<code>GIT_LFS_SKIP_SMUDGE=1 git clone</code> sequence for new automation:

~~~bash
crab lfs clone "$CRAB_LFS_REMOTE" fraud-model-client --include 'models/releases/**'
~~~

### Materialization and Git status

<code>crab lfs checkout</code> and <code>crab lfs pull</code> intentionally replace
pointer files in the worktree. With Crab 1.1.0, a direct materialization can
leave those paths reported as modified by <code>git status</code> even though the
index still contains the same pointer. This was observed and recorded during
the RustFS qualification; it does not change the downloaded bytes or the
<code>crab lfs fsck</code> result.

Before committing after an inspection-only checkout, restore pointer files
explicitly and confirm the status:

~~~bash
GIT_LFS_SKIP_SMUDGE=1 git restore --worktree -- 'models/releases/**'
git status --short
crab lfs status --porcelain
~~~

Never commit a materialized model by accident. If your workflow requires a
clean status immediately after checkout, use the standard
<code>git lfs checkout</code> path through the configured Crab transfer agent
and verify the result in a fresh clone.

## 5. Verify pointers, bytes, and refs

Run these checks before a release promotion or after a fresh clone:

~~~bash
crab lfs pointer --stdin --check --strict < <(git show HEAD:models/releases/model-v1.bin)
crab lfs fsck HEAD --pointers --objects
crab lfs status --json
git ls-remote origin refs/heads/main
~~~

The process-substitution form above works in Bash and Zsh. In a POSIX shell, use
a temporary file instead:

~~~bash
git show HEAD:models/releases/model-v1.bin > /tmp/model-v1.pointer
crab lfs pointer --stdin --check --strict < /tmp/model-v1.pointer
~~~

To prove byte identity, read the <code>oid</code> from the pointer and compare it
with the recovered file. On macOS use <code>shasum</code>; on Linux use
<code>sha256sum</code>:

~~~bash
shasum -a 256 models/releases/model-v1.bin
# Linux alternative:
sha256sum models/releases/model-v1.bin
~~~

<code>crab lfs fsck</code> verifies local object bytes and pointer references.
With a revision or range it checks every referenced object; without one it
scans the local LFS cache. Add <code>--dry-run</code> when you want corrupt
objects reported but not moved into <code>.git/lfs/bad</code>.

~~~bash
crab lfs fsck HEAD --dry-run
crab lfs fsck main~1..main --pointers --objects
~~~

## 6. Advisory locks for release files

Crab's lock commands write direct object-storage lock records; they do not
require the Git LFS HTTP locking API. A lock is advisory, so your CI and review
policy should still enforce it:

~~~bash
crab lfs lock models/releases/model-v1.bin --remote origin --expires-in 24h --json
crab lfs locks --remote origin --verify --json
crab lfs unlock models/releases/model-v1.bin --remote origin --json
~~~

Useful filters and recovery forms:

~~~bash
crab lfs locks --remote origin --path 'models/releases/model-v1.bin' --limit 20
crab lfs locks --local --json
crab lfs locks --cached --json
crab lfs unlock --remote origin --id LOCK_ID --json
crab lfs unlock --remote origin --force models/releases/model-v1.bin
~~~

<code>--verify</code> refreshes the remote result and marks locks owned by the
current Git identity. <code>--local</code> reads the local cache;
<code>--cached</code> fails when no prior remote result exists.
<code>--force</code> skips clean-worktree checks and should be used only for an
intentional administrative unlock.

## 7. Convert or migrate with a backup

There are two different operations:

- <code>crab lfs convert</code> changes the current index/worktree boundary and
  records a rollback manifest.
- <code>crab lfs migrate</code> rewrites commit history and changes every
  selected ref.

Preview a path conversion before changing anything:

~~~bash
crab lfs convert --from lfs --to xet 'models/releases/**' --dry-run
crab lfs convert --from xet --to lfs 'models/releases/**' --dry-run
~~~

Run a conversion only from a clean worktree, then verify and commit the result.
If the conversion fails, Crab rolls back automatically; an explicit rollback is
available for the last completed conversion:

~~~bash
crab lfs convert --from lfs --to xet 'models/releases/**'
crab lfs status --porcelain
crab lfs convert --rollback
~~~

For history analysis, inspect existing pointers and large files without a
rewrite:

~~~bash
crab lfs migrate info --pointers --skip-fetch --unit mb --top 20
crab lfs migrate info --above 100mb --include 'models/**' --skip-fetch
~~~

When a migration is approved, use a disposable branch, preserve an object map,
and coordinate the force-push with every consumer:

~~~bash
# Regular files -> LFS pointers; default mode rewrites selected history.
crab lfs migrate import --include 'models/**' --object-map migration.csv --yes --verbose

# Current branch only, no history rewrite; files must already match filter=lfs.
crab lfs migrate import --no-rewrite --message "track existing models" --yes models/releases/model-v1.bin

# Crab-native pointers -> LFS pointers.
crab lfs migrate import --from-crab --include 'models/**' --object-map from-crab.csv --yes

# LFS pointers -> Crab-native pointers.
crab lfs migrate export --include 'models/**' --to-crab --remote origin --object-map to-crab.csv --yes
~~~

Use <code>--everything</code>, <code>--include-ref</code>,
<code>--exclude-ref</code>, and <code>--skip-fetch</code> only after checking
the ref set. A rewritten history needs a fresh clone and
<code>crab lfs fsck</code> before it is considered complete. Never run a
migration on a shared branch merely to test the syntax.

## 8. Maintain the local and remote stores

Preview pruning before deleting anything. Remote verification is the safe
default for a shared object store:

~~~bash
crab lfs prune --dry-run --verify-remote --verbose
crab lfs prune --verify-remote --when-unverified halt --verbose
~~~

Crab protects objects reachable from commits, the index, stashes, worktrees,
recent refs, and unpushed commits. <code>--force</code> only skips confirmation;
it does not weaken those reachability checks. Do not run destructive prune while
another process is publishing a ref.

Check whether the filesystem can deduplicate checked-out files, then preview the
operation:

~~~bash
crab lfs dedup --test
crab lfs dedup --dry-run
~~~

The default deduplication is local copy-on-write working-tree management. It is
not remote object deduplication. <code>--crab-cache</code> selects Crab's legacy
cache cleanup mode; review its output before using it in automation.

~~~bash
crab lfs dedup --crab-cache --dry-run
~~~

Generate (but do not blindly apply) a cloud lifecycle policy:

~~~bash
crab lfs lifecycle-policy --backend s3 --expire-days 30 > lfs-lifecycle.json
crab lfs lifecycle-policy --backend gcs --expire-days 30 > lfs-lifecycle.json
crab lfs lifecycle-policy --backend azure --expire-days 30 > lfs-lifecycle.json
~~~

This command prints JSON; it does not mutate the bucket. Review the generated
prefix against the actual repository layout
(<code>&lt;repo-prefix&gt;/lfs/objects/</code>) and your retention policy before
applying it with the provider's control plane. Lifecycle deletion is independent
of Crab's local <code>prune</code> protection.

For support tickets, capture configuration and transfer history without
printing credentials:

~~~bash
crab lfs env
crab lfs version
crab lfs logs
crab lfs logs last
crab lfs logs --transfer-history --last 20
crab lfs ext list
~~~

<code>crab lfs logs clear</code> removes error logs but preserves transfer
history. Treat logs as potentially sensitive because paths and remote names can
be present.

~~~bash
crab lfs logs clear
~~~

## Command coverage at a glance

Every public <code>crab lfs</code> command belongs to one of these user journeys:

| Area | Commands and representative forms |
| --- | --- |
| Setup | <code>install</code>, <code>uninstall</code>, <code>update</code>, <code>clone</code> |
| Rules and pointers | <code>track</code>, <code>untrack</code>, <code>pointer</code> |
| Transfer | <code>push</code>, <code>pre-push</code>, <code>fetch</code>, <code>pull</code>, <code>checkout</code> |
| Inspection | <code>ls-files</code>, <code>status</code>, <code>fsck</code> |
| Collaboration | <code>lock</code>, <code>unlock</code>, <code>locks</code> |
| Format changes | <code>convert</code>, <code>migrate info</code>, <code>migrate import</code>, <code>migrate export</code> |
| Retention and storage | <code>prune</code>, <code>dedup</code>, <code>lifecycle-policy</code> |
| Diagnostics | <code>env</code>, <code>version</code>, <code>logs</code>, <code>ext</code>, <code>completion</code>, <code>help</code> |
| Git protocol helpers | <code>clean</code>, <code>smudge</code>, <code>filter-process</code>, <code>merge-driver</code>, <code>standalone-file</code>, <code>post-checkout</code>, <code>post-commit</code>, <code>post-merge</code> |

The helper endpoints are normally called by Git after <code>install</code>; they
are listed here so an operator can recognize them in Git config and hook traces:

~~~bash
crab lfs clean [PATH]                 # content -> pointer, stdin -> stdout
crab lfs smudge [PATH]                # pointer -> content, stdin -> stdout
crab lfs smudge --skip [PATH]         # leave pointer unchanged
crab lfs filter-process [--skip]      # Git packet-line process protocol
crab lfs pre-push                     # hook reads Git's ref-update stdin
crab lfs post-checkout [ARGS...]
crab lfs post-commit [ARGS...]
crab lfs post-merge [ARGS...]
crab lfs standalone-file              # JSON-lines transfer endpoint
crab lfs merge-driver --ancestor A --current B --other C --output D
crab lfs completion zsh > _crab       # bash, zsh, fish, or powershell
~~~

Do not call protocol helpers as a replacement for <code>crab lfs push</code> or
<code>crab lfs fetch</code>; Git supplies their stdin protocol and lifecycle.

## RustFS verification record

The cookbook was added only after the following local evidence completed
successfully in a disposable RustFS bucket. The qualification used the existing
Crab LFS qualification harness and then ran direct Crab commands against the
same repository and endpoint. The harness report stayed outside this Git
repository.

| Capability | Evidence | Result |
| --- | --- | --- |
| Remote boundary | <code>crab init --storage-provider s3</code>, Git remote discovery, <code>.crab.toml</code> | Passed |
| Local integration | <code>crab lfs install --local --skip-repo</code>, Git LFS filter/transfer-agent config | Passed |
| Pointer creation | <code>git lfs track</code>, <code>crab lfs pointer --file</code>, strict stdin validation | Passed |
| Publish path | Git LFS pre-push upload followed by <code>git push</code>; direct <code>crab lfs push</code> after initialization plus dry-run/all previews | Passed |
| Remote read path | Crab-only clone, <code>crab lfs fetch --json</code>, selective <code>checkout</code>, full <code>pull</code> | Passed; SHA-256 and byte identity matched |
| Inventory and state | <code>crab lfs ls-files --long --size --json</code>, <code>status --json/--porcelain</code> | Passed |
| Integrity | <code>git lfs fsck</code>, <code>crab lfs fsck HEAD --pointers --objects</code> | Passed; 4/4 pointers and objects verified |
| Safe retention | <code>crab lfs prune --dry-run --verify-remote</code>, <code>dedup --dry-run --test</code> | Passed; no deletion performed |
| Locks | Remote <code>lock</code>, <code>locks --verify</code>, <code>unlock</code>; local lock listing | Passed |
| Conversion preview | <code>crab lfs convert --from lfs --to xet --dry-run</code> | Passed; 4 files identified |
| History inspection | <code>crab lfs migrate info --pointers --skip-fetch --unit mb</code> | Passed; 4 pointers listed |
| Policy/diagnostics | <code>lifecycle-policy</code>, <code>env</code>, <code>version</code>, <code>logs</code>, <code>ext</code>, <code>completion</code> | Passed; policy generation is review-only |
| Destructive rewrites | <code>migrate import/export</code>, non-dry-run <code>convert</code>, deleting <code>prune</code> | Not run in smoke; use a disposable branch and backup |
| Protocol endpoints | <code>clean</code>, <code>smudge</code>, <code>filter-process</code>, hooks, merge driver | Installed/covered indirectly; Git owns their stdin protocol |

Workload: four deterministic 1 MiB files, two commits, four paths, one
RustFS S3-compatible endpoint, and a fresh clone. The ref in the clone matched
the source ref, and each recovered file's SHA-256 matched its committed LFS
pointer. This validates the direct-storage path; it is not a claim that a
four-file fixture represents production scale.

## Troubleshooting checklist

- **<code>git clone</code> cannot find <code>git-remote-crab</code>:** install
  Crab normally or put the Crab installation directory containing
  <code>git-remote-crab</code> on <code>PATH</code>.
- **<code>crab lfs install</code> refuses to update a hook:** inspect the
  existing <code>.git/hooks/pre-push</code>; merge the Crab command or use
  <code>--force</code> only after accepting the replacement.
- **A clone has pointers but no bytes:** run
  <code>crab lfs fetch origin &lt;ref&gt;</code> and then
  <code>crab lfs checkout &lt;paths&gt;</code>, or use
  <code>crab lfs pull origin</code>.
- **An object is missing locally:** run <code>crab lfs fsck &lt;ref&gt;</code>,
  fetch it again, and check that include/exclude settings are not filtering it
  out.
- **<code>git status</code> shows a model modified after
  <code>crab lfs pull</code>:** this is the Crab 1.1.0 materialization behavior
  described above; restore pointers with
  <code>GIT_LFS_SKIP_SMUDGE=1 git restore --worktree -- &lt;paths&gt;</code>
  before committing.
- **Remote operations fail against RustFS:** confirm the endpoint, region,
  path-style setting, bucket, and credential environment in
  <code>crab lfs env</code>.
- **A migration is unexpectedly broad:** stop, inspect remote-tracking refs,
  and rerun <code>migrate info</code> with explicit
  <code>--include-ref</code>/<code>--exclude-ref</code> on a disposable branch.

For the normative command contract, see Crab's
[LFS getting-started guide](https://crab.build/docs/cli/getting-started/crab-lfs),
[LFS reference](https://crab.build/docs/cli/reference/crab-lfs), and
[compatibility guide](https://crab.build/docs/cli/virtual-filesystem/lfs-compatibility).
