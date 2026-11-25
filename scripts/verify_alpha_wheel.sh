#!/usr/bin/env bash
# Verify the exact locally built wheel and installed package before owner testing.
set -euo pipefail
if [[ $# -ne 6 ]]; then
    echo "Usage: bash verify_alpha_wheel.sh PYTHON WHEEL SHA256 MANIFEST CORE_VERSION PYTHON_VERSION" >&2
    exit 2
fi
python_bin="$1"
shift
"$python_bin" -I - "$@" <<'PY'
"""Validate installed bytes against a trusted locally built wheel."""

import hashlib
import importlib.util
import json
import sys
from importlib.metadata import distribution, version
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

wheel, expected_hash, manifest_path, core_version, python_version = sys.argv[1:]
prefix = Path(sys.prefix).resolve()
assert sys.prefix != sys.base_prefix, "Use a dedicated virtual environment."
assert ".".join(map(str, sys.version_info[:3])) == python_version, "Python pin mismatch."
assert version("homeassistant") == core_version, "Core pin mismatch."
with Path(wheel).open("rb") as stream:
    actual_hash = hashlib.file_digest(stream, "sha256").hexdigest()
assert actual_hash == expected_hash, "Local wheel SHA256 mismatch."
manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
api_version = manifest["version"]
assert manifest["requirements"] == [f"ned-api=={api_version}"], "Manifest pin mismatch."
dist = distribution("ned-api")
assert dist.version == api_version, "Installed API version mismatch."
package = Path(dist.locate_file("ned_api")).resolve()
assert package.is_relative_to(prefix), "API distribution is outside the test venv."
spec = importlib.util.find_spec("ned_api")
assert spec is not None and spec.origin is not None, "API import unavailable."
assert Path(spec.origin).resolve() == package / "__init__.py", "API import shadowed."
with ZipFile(wheel) as archive:
    files = [name for name in archive.namelist() if name.startswith("ned_api/") and not name.endswith("/")]
    assert len(files) == len(set(files)), "Duplicate archive members."
    assert "ned_api/__init__.py" in files and "ned_api/py.typed" in files
    for name in files:
        relative = PurePosixPath(name).relative_to("ned_api")
        assert ".." not in relative.parts, "Unsafe wheel member."
        target = package.joinpath(*relative.parts)
        assert target.is_file() and target.resolve().is_relative_to(package)
        assert target.read_bytes() == archive.read(name), "Installed wheel bytes differ."
    installed = {
        f"ned_api/{path.relative_to(package).as_posix()}"
        for path in package.rglob("*")
        if path.is_file() and "__pycache__" not in path.relative_to(package).parts
    }
    assert installed == set(files), "Unexpected installed package files."
print("Verified local wheel SHA256, manifest pin, installed bytes and import location.")
PY
