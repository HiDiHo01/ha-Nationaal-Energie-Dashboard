#!/usr/bin/env bash
# Prepare or launch a local-only alpha with an exact checkout and no index fallback.
set -euo pipefail
if [[ $# -ne 4 || ( "$1" != prepare && "$1" != launch ) ]]; then
    echo "Usage: bash scripts/run_local_alpha.sh {prepare|launch} TEST_VENV_PYTHON TEST_CONFIG FULL_COMMIT_SHA" >&2
    exit 2
fi
mode="$1"
runtime="$2"
config="$3"
expected_commit="$4"
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
[[ "$runtime" = /* && "$config" = /* && -x "$runtime" ]]
[[ "$expected_commit" =~ ^[0-9a-f]{40}$ ]]
[[ "$(git rev-parse HEAD)" == "$expected_commit" ]]
git diff --quiet HEAD --
# Archive tracked files, not untracked or editable source.
work="$(mktemp -d)"
trap 'rm -rf -- "$work"' EXIT
git archive "$expected_commit" packages/ned-api custom_components/nationaal_energie_dashboard hacs.json .python-version | tar -x -C "$work"
unset PYTHONPATH PYTHONHOME VIRTUAL_ENV UV_PROJECT_ENVIRONMENT
export UV_PYTHON_DOWNLOADS=never
core_version=$("$runtime" -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["homeassistant"])' "$work/hacs.json")
python_version=$(cat "$work/.python-version")
"$runtime" -I -c 'import sys; from importlib.metadata import version; assert sys.prefix != sys.base_prefix; assert ".".join(map(str,sys.version_info[:3])) == sys.argv[1]; assert version("homeassistant") == sys.argv[2]' "$python_version" "$core_version"
manifest="$work/custom_components/nationaal_energie_dashboard/manifest.json"
api_version=$("$runtime" -I -c 'import json,sys; m=json.load(open(sys.argv[1])); assert m["requirements"] == ["ned-api=="+m["version"]]; print(m["version"])' "$manifest")
if [[ "$mode" == prepare ]]; then
    # Refuse an existing config directory, including symlinks.
    [[ ! -e "$config" && ! -L "$config" ]] || { echo "Test config must be a new path." >&2; exit 2; }
    mkdir -p "$work/wheels"
    uv build --wheel --no-sources --out-dir "$work/wheels" "$work/packages/ned-api"
    wheel="$work/wheels/ned_api-${api_version}-py3-none-any.whl"
    test -f "$wheel"
    hash=$(sha256sum "$wheel" | cut -d ' ' -f 1)
    # The build may obtain its pinned build backend, but runtime installation is local only.
    UV_NO_INDEX=1 UV_OFFLINE=1 UV_NO_CACHE=1 uv pip install --python "$runtime" --no-index --no-deps --reinstall "$wheel"
    UV_NO_INDEX=1 UV_OFFLINE=1 UV_NO_CACHE=1 uv pip check --python "$runtime"
    bash "$root/scripts/verify_alpha_wheel.sh" "$runtime" "$wheel" "$hash" "$manifest" "$core_version" "$python_version"
    mkdir -m 700 -- "$config"
    mkdir -p "$config/.ned-alpha" "$config/custom_components"
    cp -R "$work/custom_components/nationaal_energie_dashboard" "$config/custom_components/"
    cp "$wheel" "$config/.ned-alpha/"
    printf '%s\n' "$hash" > "$config/.ned-alpha/sha256"
    printf '%s\n' "$expected_commit" > "$config/.ned-alpha/commit"
    # Localhost-only UI on a separate port. The dedicated venv must already have UI dependencies.
    printf 'default_config:\nhttp:\n  server_host: 127.0.0.1\n  server_port: 8124\n' > "$config/configuration.yaml"
    echo "Local alpha prepared; no Home Assistant process or NED request started."
    exit 0
fi
# Launch only an explicitly prepared isolated config from the same commit.
[[ ! -L "$config" && -d "$config/.ned-alpha" ]]
[[ "$(cat "$config/.ned-alpha/commit")" == "$expected_commit" ]]
wheel="$config/.ned-alpha/ned_api-${api_version}-py3-none-any.whl"
hash=$(cat "$config/.ned-alpha/sha256")
diff -qr --exclude=__pycache__ "$work/custom_components/nationaal_energie_dashboard" "$config/custom_components/nationaal_energie_dashboard"
export UV_NO_INDEX=1 UV_OFFLINE=1 UV_NO_CACHE=1
uv pip check --python "$runtime"
bash "$root/scripts/verify_alpha_wheel.sh" "$runtime" "$wheel" "$hash" "$manifest" "$core_version" "$python_version"
# No package-manager fallback, even if a requirement is absent. Missing UI dependencies fail.
cd "$config"
"$runtime" -I -m homeassistant --config "$config" --skip-pip
