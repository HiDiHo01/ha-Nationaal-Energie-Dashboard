#!/usr/bin/env bash
# Exercise the actual workflow shell blocks with synthetic GitHub responses.
set -euo pipefail

root=$(cd -- "$(dirname -- "$0")/.." && pwd)
workflow="$root/.github/workflows/dependabot-automerge.yaml"
tmp=$(mktemp -d)
trap 'rm -rf -- "$tmp"' EXIT
mkdir "$tmp/bin"

# Fail closed if the workflow no longer contains exactly two inline run blocks.
awk -v dir="$tmp" '
    /^        run: \|$/ { count++; active=1; next }
    active && /^          / { print substr($0, 11) > (dir "/step-" count); next }
    active && /^$/ { next }
    { active=0 }
    END { if (count != 2) exit 1 }
' "$workflow"
for step in "$tmp/step-1" "$tmp/step-2"; do
    test -s "$step"
    bash -n "$step"
done

# No real gh, network tools or inherited credentials in the child environment.
for tool in bash jq grep tr seq; do
    ln -s "$(command -v "$tool")" "$tmp/bin/$tool"
done
cat > "$tmp/bin/gh" <<'MOCK'
#!/usr/bin/env bash
set -euo pipefail
case "$*" in
    'api repos/synthetic/repo/pulls/7 --jq .head.sha') printf '%s\n' "$CURRENT_SHA" ;;
    'api --paginate --slurp repos/synthetic/repo/pulls/7/files?per_page=100') printf '%s\n' "$FILES" ;;
    'pr checks 7 --repo synthetic/repo --required --json name,bucket')
        printf '%s\n' "$CHECKS"
        exit "$CHECK_EXIT" ;;
    'pr merge 7 --repo synthetic/repo --squash --match-head-commit synthetic-head')
        printf '%s\n' 'merge' >> "$MERGE_LOG" ;;
    *) printf 'Unexpected mock gh invocation\n' >&2; exit 97 ;;
esac
MOCK
cat > "$tmp/bin/sleep" <<'MOCK'
#!/usr/bin/env bash
exit 0
MOCK
chmod +x "$tmp/bin/gh" "$tmp/bin/sleep"

count=0
lock='[[{"filename":"uv.lock","status":"modified"}]]'
manifest='[[{"filename":"pyproject.toml","status":"modified"}]]'
both='[[{"filename":"pyproject.toml","status":"modified"},{"filename":"uv.lock","status":"modified"}]]'
pass='[{"name":"Home Assistant production baseline","bucket":"pass"},{"name":"hassfest","bucket":"pass"}]'
pending='[{"name":"Home Assistant production baseline","bucket":"pending"},{"name":"hassfest","bucket":"pass"}]'
fail='[{"name":"Home Assistant production baseline","bucket":"fail"},{"name":"hassfest","bucket":"pass"}]'
cancel='[{"name":"Home Assistant production baseline","bucket":"cancel"},{"name":"hassfest","bucket":"pass"}]'
missing='[{"name":"Home Assistant production baseline","bucket":"pass"}]'
pin=$(jq -cn '[[{filename:".github/workflows/ci.yaml",status:"modified",patch:("-        uses: owner/action@"+ ("a"*40)+"\n+        uses: owner/action@"+ ("b"*40))}]]')
logic=$(jq -cn '[[{filename:".github/workflows/ci.yaml",status:"modified",patch:"-        run: false\n+        run: true"}]]')
changed_action=$(jq -cn '[[{filename:".github/workflows/ci.yaml",status:"modified",patch:("-        uses: owner/action@"+ ("a"*40)+"\n+        uses: other/action@"+ ("b"*40))}]]')

# Arguments: step, current revision, update type, dependencies, maintainer changes,
# changed files, required checks, simulated gh checks exit status.
run_step() {
    local step=$1
    shift
    env -i PATH="$tmp/bin" GITHUB_REPOSITORY=synthetic/repo PR_NUMBER=7 \
        HEAD_SHA=synthetic-head CURRENT_SHA="$1" UPDATE_TYPE="$2" \
        DEPENDENCIES="$3" MAINTAINER_CHANGES="$4" FILES="$5" CHECKS="$6" \
        CHECK_EXIT="$7" GITHUB_OUTPUT="$tmp/output" MERGE_LOG="$tmp/merge" \
        "$tmp/bin/bash" "$tmp/step-$step"
}

classify() {
    local name=$1 expected=$2
    shift 2
    : > "$tmp/output"
    : > "$tmp/merge"
    if ! run_step 1 "$@" "$pass" 0 > "$tmp/log" 2>&1; then
        printf 'FAIL classify %s\n' "$name" >&2
        cat "$tmp/log" >&2
        exit 1
    fi
    if [[ $(tail -n 1 "$tmp/output") != "eligible=$expected" || -s "$tmp/merge" ]]; then
        printf 'FAIL classify %s\n' "$name" >&2
        cat "$tmp/log" >&2
        exit 1
    fi
    count=$((count + 1))
    printf 'PASS classify %s\n' "$name"
}

merge_case() {
    local name=$1 expected_status=$2 expected_merge=$3 current=$4 checks=$5 check_exit=$6
    local status=0
    : > "$tmp/merge"
    run_step 2 "$current" version-update:semver-patch aiohttp false "$lock" \
        "$checks" "$check_exit" > "$tmp/log" 2>&1 || status=$?
    if [[ $status != "$expected_status" || $(wc -l < "$tmp/merge") -ne $expected_merge ]]; then
        printf 'FAIL merge %s (exit %s)\n' "$name" "$status" >&2
        cat "$tmp/log" >&2
        exit 1
    fi
    count=$((count + 1))
    printf 'PASS merge %s\n' "$name"
}

classify patch true synthetic-head version-update:semver-patch aiohttp false "$lock"
classify minor true synthetic-head version-update:semver-minor aiohttp false "$both"
classify pin true synthetic-head version-update:semver-patch owner/action false "$pin"
classify major false synthetic-head version-update:semver-major aiohttp false "$lock"
classify unknown false synthetic-head unknown aiohttp false "$lock"
classify core false synthetic-head version-update:semver-patch homeassistant false "$lock"
classify paired-core false synthetic-head version-update:semver-patch 'aiohttp, pytest_homeassistant' false "$lock"
classify missing-metadata false synthetic-head version-update:semver-patch '' false "$lock"
classify maintainer false synthetic-head version-update:semver-patch aiohttp true "$lock"
classify changed-head false another-head version-update:semver-patch aiohttp false "$lock"
classify missing-lock false synthetic-head version-update:semver-patch aiohttp false "$manifest"
classify unexpected-file false synthetic-head version-update:semver-patch aiohttp false '[[{"filename":"scripts/example.py","status":"modified"}]]'
classify added-file false synthetic-head version-update:semver-patch aiohttp false '[[{"filename":"uv.lock","status":"added"}]]'
classify empty-files false synthetic-head version-update:semver-patch aiohttp false '[[]]'
classify workflow-logic false synthetic-head version-update:semver-patch owner/action false "$logic"
classify changed-action false synthetic-head version-update:semver-patch owner/action false "$changed_action"
merge_case passed 0 1 synthetic-head "$pass" 0
merge_case failed 1 0 synthetic-head "$fail" 1
merge_case cancelled 1 0 synthetic-head "$cancel" 1
merge_case pending 1 0 synthetic-head "$pending" 8
merge_case missing-required 1 0 synthetic-head "$missing" 0
merge_case empty-checks 1 0 synthetic-head '' 1
merge_case changed-head 0 0 another-head "$pass" 0
printf 'All %s synthetic Dependabot scenarios passed; no real merge executed.\n' "$count"
