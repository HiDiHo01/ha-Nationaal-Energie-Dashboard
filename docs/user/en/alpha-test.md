# Local alpha test 0.1.0a1

This test is intended only for a separate, already working Home Assistant Core test environment with Core 2026.11.3 and Python 3.14.10. Do not install on the production environment, through HACS or from a public index. Start owner testing only after all required CI checks pass on the exact commit under test. There is no public release or PyPI publication.

## Preparation and installation

Verify the checkout provenance and exact commit in PR #39; run the following commands from the repository root on the test machine. Set both paths to your separate test environment (not production).

```bash
HA_PYTHON="/path/to/test-venv/bin/python"
HA_CONFIG="/path/to/test-config"
"$HA_PYTHON" -c 'import sys; from importlib.metadata import version; assert sys.version_info[:3] == (3, 14, 10); assert version("homeassistant") == "2026.11.3"'
uv build --wheel --no-sources --out-dir wheelhouse packages/ned-api
sha256sum wheelhouse/ned_api-0.1.0a1-py3-none-any.whl
uv pip install --python "$HA_PYTHON" --no-index --no-deps --reinstall wheelhouse/ned_api-0.1.0a1-py3-none-any.whl
uv pip check --python "$HA_PYTHON"
"$HA_PYTHON" -c 'from importlib.metadata import version; assert version("ned-api") == "0.1.0a1"; import ned_api; print(ned_api.__file__)'
mkdir -p "$HA_CONFIG/custom_components"
cp -R custom_components/nationaal_energie_dashboard "$HA_CONFIG/custom_components/"
```

Use a clean test configuration without an older copy of the integration. Build the wheel yourself from the same commit, record the hash and do not install a similarly named package from a public index. The locked development environment and [native wheel probe](../../../scripts/check_runtime_distribution.sh) are the dependency compatibility reference. Stop on missing or conflicting dependencies. The alpha assumes Home Assistant and its other requirements are installed; HA OS/Supervised and HACS installation are not yet validated. Restart the test instance with `UV_NO_INDEX=1 UV_OFFLINE=1` to prevent external package resolution during this test.

## Functional owner test

1. Open Settings > Devices & services > Add integration > Nationaal Energie Dashboard. Enter only your own valid API key into the masked field; do not share it. One positive historical solar query validates access.
2. Check the five sensors: solar, onshore wind, offshore wind, national consumption and national production. Compare units (native kW, suggested MW), validity intervals and values with NED. Current may include upstream estimates.
3. Verify that absent, invalid or stale values become unavailable rather than zero. Each refresh sends at most five requests, or ten when UTC days overlap. Five minutes between regular updates; no application retries. Stop on unusual behavior or HTTP 429; do not conduct negative or load probes.
4. Test reload and unload in the test environment and verify polling stops. Share only sanitized errors, status codes and observations; no credentials, raw response bodies or configuration storage.

CO₂, forecast and estimated renewable share are not registered in this alpha. Daily aggregation, revision handling, full permission semantics and universal rate-limit guarantees remain unconfirmed. The 30-minute stale limit and process-local budget are conservative design choices. A successful owner test is not full phase acceptance or a production release.
