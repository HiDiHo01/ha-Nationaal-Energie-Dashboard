#!/usr/bin/env bash
# BL-006: isolated synthetic and actual wheels through the real HA requirements manager.
set -euo pipefail

root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
work="$(mktemp -d)"
trap 'rm -rf -- "$work"' EXIT
export UV_PYTHON_DOWNLOADS=never
unset PYTHONPATH PYTHONHOME VIRTUAL_ENV UV_PROJECT_ENVIRONMENT
python_bin="$(command -v python)"
"$python_bin" -I -c 'import sys; from pathlib import Path; assert ".".join(map(str, sys.version_info[:3])) == Path(".python-version").read_text().strip()'
UV_PROJECT_ENVIRONMENT="$work/venv" uv sync --locked --python "$python_bin" --project "$root"
runtime="$work/venv/bin/python"
mkdir -p "$work/project/src/ned_api_runtime_probe" "$work/wheelhouse" "$work/config/custom_components"
cp -R "$root/custom_components/nationaal_energie_dashboard" "$work/config/custom_components/"
find "$work/config/custom_components" -type d -name __pycache__ -prune -exec rm -rf {} +
cp LICENSE "$work/project/LICENSE"
cat > "$work/project/pyproject.toml" <<'TOML'
[build-system]
requires = ["uv_build==0.13.9"]
build-backend = "uv_build"

[project]
name = "ned-api-runtime-probe"
version = "0.0.1"
description = "Synthetic local-only Home Assistant runtime packaging probe"
requires-python = ">=3.14.2"
license = "GPL-3.0-only"
license-files = ["LICENSE"]
dependencies = ["aiohttp>=3.14.5,<4"]
TOML
cat > "$work/project/src/ned_api_runtime_probe/__init__.py" <<'PY'
"""Synthetic package for local wheel installation verification."""

from aiohttp import ClientSession


def session_type() -> type[ClientSession]:
    """Return the async dependency type without opening a session."""
    return ClientSession
PY
touch "$work/project/src/ned_api_runtime_probe/py.typed"
uv build --wheel --no-sources --out-dir "$work/wheelhouse" "$work/project"
wheel="$work/wheelhouse/ned_api_runtime_probe-0.0.1-py3-none-any.whl"
test -f "$wheel"
sha256sum "$wheel"

# Build the actual package before switching the installer to offline mode.
cmp LICENSE packages/ned-api/LICENSE
api_version=$("$runtime" -I -c 'import tomllib; from pathlib import Path; project = tomllib.loads(Path("packages/ned-api/pyproject.toml").read_text())["project"]; assert project["name"] == "ned-api"; print(project["version"])')
uv build --wheel --no-sources --out-dir "$work/wheelhouse" packages/ned-api
api_wheel="$work/wheelhouse/ned_api-${api_version}-py3-none-any.whl"
test -f "$api_wheel"
sha256sum "$api_wheel"

# Only the temporary wheelhouse is available to HA's real uv installer.
# No editable package, source-tree import, external index or publish action.
cd "$work"
export UV_NO_INDEX=1 UV_OFFLINE=1 UV_NO_CACHE=1
export UV_FIND_LINKS="$work/wheelhouse"
"$runtime" -I - "$work/config" "$root/hacs.json" "$api_version" <<'PY'
"""Exercise the exact Core requirements manager with uninstalled wheels."""
import asyncio
import importlib
import importlib.util
import json
import sys
from importlib.metadata import distribution, distributions, version
from pathlib import Path

from aiohttp import ClientSession
from homeassistant.core import HomeAssistant
from homeassistant.requirements import async_process_requirements

assert version("homeassistant") == json.loads(Path(sys.argv[2]).read_text())["homeassistant"]
assert importlib.util.find_spec("ned_api_runtime_probe") is None
assert importlib.util.find_spec("ned_api") is None
before = {item.metadata["Name"]: item.version for item in distributions()}
api_version = sys.argv[3]
config_dir = Path(sys.argv[1]).resolve()
manifest_path = config_dir / "custom_components/nationaal_energie_dashboard/manifest.json"
manifest = json.loads(manifest_path.read_text())
assert manifest["requirements"] == [f"ned-api=={api_version}"]
assert manifest["version"] == api_version


async def main() -> None:
    """Install pinned packages using the native custom integration path."""
    hass = HomeAssistant(sys.argv[1])
    await async_process_requirements(
        hass, "ned_api_runtime_probe", ["ned-api-runtime-probe==0.0.1"], is_built_in=False
    )
    await async_process_requirements(
        hass, "nationaal_energie_dashboard", manifest["requirements"], is_built_in=False
    )
    importlib.invalidate_caches()
    api_module = importlib.import_module("ned_api")
    async with ClientSession() as session:
        transport = api_module.NedTransport(session, "https://example.invalid")
        assert str(transport.origin) == "https://example.invalid"
        assert not session.closed
    # Import the copied integration, never the repository checkout or an editable API.
    sys.path.insert(0, str(config_dir))
    component = importlib.import_module("custom_components.nationaal_energie_dashboard")
    assert Path(component.__file__).resolve().is_relative_to(config_dir)
    flow_module = importlib.import_module("custom_components.nationaal_energie_dashboard.config_flow")
    sensor_module = importlib.import_module("custom_components.nationaal_energie_dashboard.sensor")
    assert callable(component.async_setup_entry)
    assert callable(flow_module.NedConfigFlow.async_step_user)
    assert callable(sensor_module.async_setup_entry)
    print("Copied alpha integration and manifest-pinned dependency import passed.")


asyncio.run(main())
importlib.invalidate_caches()
module = importlib.import_module("ned_api_runtime_probe")
assert version("ned-api-runtime-probe") == "0.0.1"
assert Path(module.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
assert module.session_type() is ClientSession
assert Path(module.__file__).with_name("py.typed").is_file()
print("Native HA synthetic requirement install, isolated import and typing marker passed.")

api_module = importlib.import_module("ned_api")
api_dist = distribution("ned-api")
assert api_dist.version == api_version
assert api_dist.metadata["License-Expression"] == "GPL-3.0-only"
assert Path(api_module.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
assert Path(api_module.__file__).with_name("py.typed").is_file()
assert any(str(path).endswith(".dist-info/licenses/LICENSE") for path in api_dist.files or ())
assert issubclass(api_module.NedConnectionError, api_module.NedApiError)
after = {item.metadata["Name"]: item.version for item in distributions()}
assert all(after.get(name) == installed_version for name, installed_version in before.items())
assert set(after) - set(before) == {"ned-api", "ned-api-runtime-probe"}
print("Native HA actual API wheel install, dependency preservation, typed import and session injection passed.")
PY
uv pip check --python "$runtime"
# Verify the actual installed wheel bytes with the same owner-test preflight.
api_hash=$(sha256sum "$api_wheel" | cut -d ' ' -f 1)
core_version=$("$runtime" -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["homeassistant"])' "$root/hacs.json")
python_version=$(cat "$root/.python-version")
manifest_path="$work/config/custom_components/nationaal_energie_dashboard/manifest.json"
bash -n "$root/scripts/run_local_alpha.sh"
bash -n "$root/scripts/verify_alpha_wheel.sh"
bash "$root/scripts/verify_alpha_wheel.sh" "$runtime" "$api_wheel" "$api_hash" "$manifest_path" "$core_version" "$python_version"
if bash "$root/scripts/verify_alpha_wheel.sh" "$runtime" "$api_wheel" "invalid-hash" "$manifest_path" "$core_version" "$python_version"; then
    echo "Unexpected acceptance of invalid wheel hash" >&2
    exit 1
fi
echo "Alpha preflight rejects invalid wheel hash."
echo "Synthetic and actual runtime wheel probes passed; copied alpha imports passed; full live setup is not evaluated."

# R39-11: Core loads default integrations even with an HTTP-only YAML file.
# Extend only this disposable venv, after proving the locked wheel installation.
# Read requirements from the installed, exact Core release, including its
# dependency and after-dependency closure. Preserve every existing version.
"$runtime" -I - "$work" <<'PY'
"""Collect the pinned Core startup dependencies and preserve the baseline."""

import json
import sys
from importlib.metadata import distributions
from pathlib import Path

import homeassistant
from homeassistant.bootstrap import CORE_INTEGRATIONS, DEFAULT_INTEGRATIONS
from homeassistant.const import BASE_PLATFORMS
from packaging.requirements import Requirement

work = Path(sys.argv[1])
core_dir = Path(homeassistant.__file__).resolve().parent
pending = set(CORE_INTEGRATIONS) | set(DEFAULT_INTEGRATIONS) | set(BASE_PLATFORMS)
pending.add("http")
seen: set[str] = set()
requirements: set[str] = set()
while pending:
    domain = pending.pop()
    if domain in seen:
        continue
    seen.add(domain)
    manifest_path = core_dir / "components" / domain / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["domain"] == domain, f"Unexpected Core manifest: {domain}"
    pending.update(set(manifest.get("dependencies", ())) - seen)
    pending.update(set(manifest.get("after_dependencies", ())) - seen)
    for raw in manifest.get("requirements", ()):
        requirement = Requirement(raw)
        assert requirement.url is None, f"Unexpected direct URL in {domain}"
        requirements.add(str(requirement))
assert any(item.startswith("home-assistant-frontend==") for item in requirements)
(work / "startup-requirements.txt").write_text(
    "\n".join(sorted(requirements)) + "\n", encoding="utf-8"
)
baseline = {item.metadata["Name"]: item.version for item in distributions()}
(work / "startup-baseline.json").write_text(json.dumps(baseline), encoding="utf-8")
(work / "startup-baseline.txt").write_text(
    "".join(f"{name}=={version}\n" for name, version in sorted(baseline.items())),
    encoding="utf-8",
)
(work / "core-constraints-path").write_text(
    str(core_dir / "package_constraints.txt"), encoding="utf-8"
)
print(f"Resolved {len(seen)} Core manifests and {len(requirements)} startup requirements.")
PY
# Package downloads are allowed only during dependency preparation, not launch.
env -u UV_NO_INDEX -u UV_OFFLINE -u UV_NO_CACHE -u UV_FIND_LINKS \
    uv pip install --python "$runtime" \
    --constraint "$(cat "$work/core-constraints-path")" \
    --constraint "$work/startup-baseline.txt" \
    --requirement "$work/startup-requirements.txt"
"$runtime" -I - "$work/startup-baseline.json" <<'PY'
"""Verify that extra Core dependencies did not replace any baseline package."""

import json
import sys
from importlib.metadata import distributions
from pathlib import Path

before = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
after = {item.metadata["Name"]: item.version for item in distributions()}
assert all(after.get(name) == version for name, version in before.items())
print(f"Preserved {len(before)} baseline distributions; added {len(after) - len(before)}.")
PY
uv pip check --python "$runtime"
# Audit the additional dependencies as well as the unchanged locked baseline.
"$runtime" -I -m pip_audit --local

# R39-11: exercise the actual launcher with no configured NED entry or credential.
# Keep the localhost configuration minimal; Core's mandatory frontend is installed.
# The full default_config and configured NED entry are not part of this test.
cd "$root"
commit=$(git rev-parse HEAD)
alpha_config="$work/alpha-config"
# Preparation may build with the pinned backend; package installation is offline.
env -u UV_NO_INDEX -u UV_OFFLINE -u UV_NO_CACHE -u UV_FIND_LINKS \
    bash scripts/run_local_alpha.sh prepare "$runtime" "$alpha_config" "$commit"
printf 'logger:\n  default: info\nhttp:\n  server_host: 127.0.0.1\n  server_port: 8124\n' > "$alpha_config/configuration.yaml"
# Tampering with the tracked integration copy must fail before Core starts.
manifest_copy="$alpha_config/custom_components/nationaal_energie_dashboard/manifest.json"
cp "$manifest_copy" "$work/manifest-original.json"
printf '\n' >> "$manifest_copy"
if bash scripts/run_local_alpha.sh launch "$runtime" "$alpha_config" "$commit"; then
    echo "Unexpected acceptance of changed manifest" >&2
    exit 1
fi
cp "$work/manifest-original.json" "$manifest_copy"
alpha_wheel="$alpha_config/.ned-alpha/ned_api-${api_version}-py3-none-any.whl"
cp "$alpha_wheel" "$work/alpha-original.whl"
printf 'tampered' >> "$alpha_wheel"
if bash scripts/run_local_alpha.sh launch "$runtime" "$alpha_config" "$commit"; then
    echo "Unexpected acceptance of changed wheel" >&2
    exit 1
fi
cp "$work/alpha-original.whl" "$alpha_wheel"

alpha_pid=""
cleanup_alpha() {
    if [[ -n "$alpha_pid" ]]; then
        kill -TERM "$alpha_pid" 2>/dev/null || true
        wait "$alpha_pid" 2>/dev/null || true
    fi
    rm -rf -- "$work"
}
trap cleanup_alpha EXIT
for cycle in 1 2; do
    bash scripts/run_local_alpha.sh launch "$runtime" "$alpha_config" "$commit" \
        > "$work/core-${cycle}.log" 2>&1 &
    alpha_pid=$!
    ready=false
    for _ in $(seq 1 60); do
        if ! kill -0 "$alpha_pid" 2>/dev/null; then
            cat "$work/core-${cycle}.log"
            exit 1
        fi
        if grep -Fq 'Home Assistant initialized in' "$work/core-${cycle}.log" && \
            curl --noproxy '*' --fail --silent --max-time 1 --output /dev/null http://127.0.0.1:8124/; then
            ready=true
            break
        fi
        sleep 1
    done
    if [[ "$ready" != true ]]; then
        cat "$work/core-${cycle}.log"
        exit 1
    fi
    if grep -Eq 'Activating recovery mode|Starting in recovery mode|Setup failed for|Error during setup of component' "$work/core-${cycle}.log"; then
        cat "$work/core-${cycle}.log"
        exit 1
    fi
    kill -TERM "$alpha_pid"
    # Bound process shutdown without leaving a test Core instance running.
    for _ in $(seq 1 30); do
        kill -0 "$alpha_pid" 2>/dev/null || break
        sleep 1
    done
    if kill -0 "$alpha_pid" 2>/dev/null; then
        kill -KILL "$alpha_pid"
        echo "Core shutdown exceeded the test deadline" >&2
        exit 1
    fi
    wait "$alpha_pid"
    alpha_pid=""
done
echo "Local alpha prepare/start/stop/restart passed with mandatory Core frontend and minimal localhost configuration; no NED entry."
