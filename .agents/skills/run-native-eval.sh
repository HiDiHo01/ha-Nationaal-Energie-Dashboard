#!/usr/bin/env bash
# Run one opt-in Codex skill evaluation in an isolated repository snapshot.
set -euo pipefail
umask 077

if [[ $# -ne 2 || ! "$1" =~ ^(NL|EN|NEG)[0-9]{2}$ ]]; then
  echo 'Usage: bash .agents/skills/run-native-eval.sh CASE_ID /absolute/private/output-directory' >&2
  exit 2
fi
case_id=$1
output_dir=$2
if [[ "$output_dir" != /* || ! -d "$output_dir" ]]; then
  echo 'Use an existing private output directory with an absolute path.' >&2
  exit 2
fi
root=$(git rev-parse --show-toplevel)
output_dir=$(cd "$output_dir" && pwd -P)
root=$(cd "$root" && pwd -P)
if [[ "$output_dir" == "$root" || "$output_dir" == "$root/"* ]]; then
  echo 'Keep evaluation traces outside the repository.' >&2
  exit 2
fi
if ! command -v codex >/dev/null; then
  echo 'BLOCKED: install and authenticate Codex CLI in an authorized environment.' >&2
  exit 3
fi
commit=$(git -C "$root" rev-parse HEAD)
prompt=$(git -C "$root" show "$commit:.agents/skills/ACTIVATION_EVALS.md" | awk -F '|' -v id="$case_id" '$2 == " " id " " {sub(/^ /, "", $3); sub(/ $/, "", $3); print $3}')
if [[ -z "$prompt" || "$prompt" == *$'\n'* ]]; then
  echo "Unknown or ambiguous scenario: $case_id" >&2
  exit 2
fi
run_dir=$(mktemp -d "$output_dir/$case_id.XXXXXXXX")
workspace=$(mktemp -d)
trap 'rm -rf -- "$workspace"' EXIT
# Export committed content only; no untracked files or Git remotes.
git -C "$root" archive "$commit" | tar -x -C "$workspace"
git -C "$workspace" init -q --template=
git -C "$workspace" add -f -- .
git -C "$workspace" -c user.name='Skill evaluation' -c user.email='eval@example.invalid' -c commit.gpgsign=false -c core.hooksPath=/dev/null commit -qm 'Evaluation snapshot'
{
  printf 'scenario=%s\nsource_commit=%s\nprompt=%s\n' "$case_id" "$commit" "$prompt"
  codex --version
} > "$run_dir/metadata.txt"
snapshot=$(git -C "$workspace" rev-parse HEAD)
# No approval escalation; no repository remote; disable sandbox network access.
set +e
(cd "$workspace" && codex --ask-for-approval never exec --sandbox workspace-write -c sandbox_workspace_write.network_access=false --json "$prompt" </dev/null) > "$run_dir/trace.jsonl" 2> "$run_dir/stderr.log"
status=$?
set -e
printf 'exit_status=%s\n' "$status" >> "$run_dir/metadata.txt"
git -C "$workspace" status --short > "$run_dir/worktree-status.txt"
git -C "$workspace" add -N -- .
git -C "$workspace" diff "$snapshot" -- > "$run_dir/worktree.diff"
printf 'Evidence: %s\n' "$run_dir"
echo 'Review trace and worktree diff before scoring; an exit code alone is not a pass.'
exit "$status"
