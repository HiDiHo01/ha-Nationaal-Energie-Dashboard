#!/usr/bin/env bash
# BL-006: isolated synthetic wheel through the real HA requirements manager.
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
mkdir -p "$work/project/src/ned_api_runtime_probe" "$work/wheelhouse" "$work/config"
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

# Only the temporary wheelhouse is available to HA's real uv installer.
# No editable package, source-tree import, external index or publish action.
cd "$work"
export UV_NO_INDEX=1 UV_OFFLINE=1 UV_NO_CACHE=1
export UV_FIND_LINKS="$work/wheelhouse"
"$runtime" -I - "$work/config" "$root/hacs.json" <<'PY'
"""Exercise the exact Core requirements manager with an uninstalled wheel."""
import asyncio
import importlib
import importlib.util
import json
import sys
from importlib.metadata import version
from pathlib import Path

from aiohttp import ClientSession
from homeassistant.core import HomeAssistant
from homeassistant.requirements import async_process_requirements

assert version("homeassistant") == json.loads(Path(sys.argv[2]).read_text())["homeassistant"]
assert importlib.util.find_spec("ned_api_runtime_probe") is None
before = version("aiohttp")


async def main() -> None:
    """Install the pinned package using the native custom integration path."""
    hass = HomeAssistant(sys.argv[1])
    await async_process_requirements(
        hass, "ned_api_runtime_probe", ["ned-api-runtime-probe==0.0.1"], is_built_in=False
    )


asyncio.run(main())
importlib.invalidate_caches()
module = importlib.import_module("ned_api_runtime_probe")
assert version("ned-api-runtime-probe") == "0.0.1"
assert Path(module.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
assert module.session_type() is ClientSession
assert version("aiohttp") == before
assert Path(module.__file__).with_name("py.typed").is_file()
print("Native HA requirement install, pinned version, isolated import and typing marker passed.")
PY
uv pip check --python "$runtime"
echo "Synthetic runtime wheel probe passed; full integration installation is not evaluated."
