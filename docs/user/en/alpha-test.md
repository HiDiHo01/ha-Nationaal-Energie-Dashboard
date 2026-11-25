# Local alpha test 0.1.0a1

Use only a separate Home Assistant Core test environment with Core 2026.11.3 and Python 3.14.10. No HACS, HA OS/Supervised or public package index installation. Wait for all required checks on the exact tested commit and the [PR #39 review](../../PR39_REVIEW.md) to be addressed. No public release.

## Controlled preparation and launch

Use a trusted checkout of the reviewed commit and a separate, already working Core virtual environment with all UI dependencies. The configuration path must be new and absolute, with an existing parent directory. Never use the production virtual environment. Select the full 40-character commit SHA from successful CI, not an arbitrary branch version.

```bash
HA_PYTHON="/path/to/test-venv/bin/python"
HA_CONFIG="/path/to/new-test-config"
COMMIT="<full-reviewed-commit-sha>"
bash scripts/run_local_alpha.sh prepare "$HA_PYTHON" "$HA_CONFIG" "$COMMIT"
bash scripts/run_local_alpha.sh launch "$HA_PYTHON" "$HA_CONFIG" "$COMMIT"
```

The [launcher](../../../scripts/run_local_alpha.sh) uses tracked files from the exact Git commit, rejects an existing config directory during preparation, builds the wheel locally and installs only that wheel without an index, cache or dependency resolution. The [preflight](../../../scripts/verify_alpha_wheel.sh) checks Core/Python versions, SHA256, manifest pin, installed package bytes and import location. Each launch verifies the integration copy and wheel again. The locally stored hash provides provenance checking within the trusted test environment, not an independent digital signature. Launch uses UV_NO_INDEX=1, UV_OFFLINE=1, UV_NO_CACHE=1 and --skip-pip; missing UI dependencies must be installed in the test venv beforehand from trusted sources. --skip-pip is solely for this local owner test; normal CI separately exercises the actual requirements manager. The test UI binds to 127.0.0.1:8124 by default. The launch step starts Core; preparation starts no process or NED request.

## Functional owner test

1. Open the test UI: Settings > Devices & services > Add integration > Nationaal Energie Dashboard. Enter only your own valid API key into the masked field. A positive historical solar query validates access to that query, not all datasets.
2. Check the five sensors: solar, onshore wind, offshore wind, national consumption and national production. Compare native kW (suggested MW), validity boundaries, receipt time and values. Current may contain upstream estimates. Only quarters closed at both request start and receipt are eligible; never promote earlier fetched open quarters automatically.
3. Check independent availability and recovery. Failed datasets remain unavailable; other successful datasets remain usable. No zero filling. All datasets failing, HTTP 401 or 429 fails the batch; 403 remains ambiguous. The 30-minute interval cutoff remains provisional; cache callbacks make no HTTP calls. Per refresh at most five logical day queries, or ten with UTC overlap; aiohttp can internally repeat a GET. Middleware counts each attempt, including failures and internal retries. Process-local budget 120 attempts/300 seconds. HTTP 429 blocks new attempts for at least 300 seconds and honors longer valid Retry-After values; above 24 hours the process remains blocked. Do not restart to bypass a server restriction. No negative or load probes.
4. Test reload, reconfiguration and unload with normal valid credentials; stop on unusual behavior. Share only sanitized messages, status codes and observations.

## Stop and roll back

Remove the integration through the test UI, stop the separate Core process and verify it is no longer active. Optionally make a secure backup of the test configuration; it may contain credentials. Then remove only your own test configuration and separate test venv if no longer needed. The launcher does not delete existing user configuration. Do not start a production installation from this alpha.

CO₂, forecasts, estimated renewable share, daily aggregation and revision processing remain out of scope. Full permission semantics, source publication latency, upstream quota scope and formal NED Retry-After semantics remain unconfirmed. An owner test is not full phase acceptance or a production release.

R39-09–12 and CodeRabbit: periodic polling only for active entity contexts (first refresh all five), half-open 30-minute freshness window, no recovery message without a fresh closed quarter; all active datasets lacking usable readings fail the update and trigger native setup retry. HTTP asctime-date is interpreted as UTC per RFC 9110 section 5.6.7. The launcher probe uses a temporary venv and minimal localhost HTTP configuration, no NED entry or key; full frontend and owner testing remain open.
