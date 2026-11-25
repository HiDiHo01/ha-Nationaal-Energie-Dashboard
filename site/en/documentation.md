---
lang: en
title: Documentation
description: Requirements, development status and support.
permalink: /en/documentation/
other_lang: nl
other_url: /nl/documentation/
---
## Installation and requirements

Follow the local alpha test instructions in the English repository README; do not use HACS or a public package index for the alpha.

The integration is still in development. No installable release is available. Distribution through Home Assistant Marketplace is intended. GPL-3.0-only has been chosen to meet the [HACS license requirement](https://www.hacs.xyz/docs/publish/include/#check-license). GitHub license detection is confirmed; actual catalog admission remains pending. The runtime distribution strategy has been validated using a synthetic wheel; full production installation still requires verification.

The development branch contains a limited local alpha (0.1.0a1): real credential validation, an independent UTC quarter-hour parser and five national power sensors. Use only the exact matching locally built wheel for the test installation; no HACS installation or public release. CO₂, forecast and the estimated renewable share remain reserved until their contract conditions are met. CI passed on 7a5956d; the new remediation commit and live installation require separate verification; BL-003 and the general phase gates remain open.

Review remediation R39-01–08: status-first error handling, Retry-After, per-attempt budget, independent dataset availability and receipt timestamp. Use the controlled local launcher for the separate test environment. Native lifecycle and wheel preflight tests passed on 7a5956d; the new remediation requires revalidation. No new live probes or release.

R39-09–12 and CodeRabbit: periodic polling only for active entity contexts (first refresh all five), half-open 30-minute freshness window, no recovery message without a fresh closed quarter; all active datasets lacking usable readings fail the update and trigger native setup retry. HTTP asctime-date is interpreted as UTC per RFC 9110 section 5.6.7. The launcher probe uses a temporary venv and minimal localhost HTTP configuration, no NED entry or key; full frontend and owner testing remain open.

## NED API key

Three manually reported authentication observations reproduce HTTP 200 (valid key), 401 (missing) and 403 (invalid) for the same national solar query. The presumed limited key receives access; permission semantics remain open. The alpha client and Config Flow distinguish 401 from 403 without logging error payloads; local owner testing requires successful CI and the exact wheel.

For future use, create an account at [NED](https://ned.nl/), open Mijn account (My account) → API and generate a personal API key. Store it securely. Never disclose keys in issues or logs.

## API contract status

The tested national P0 quarter-hour queries have been structurally validated. The NED manual describes power (kW), interval energy (kWh), CO₂ emissions (kg) and emission factors (kg CO₂/kWh). However, the OpenAPI description specifies tonnes for emissions; the examined type-27 quarter-hour records support kg, but the formal unit remains unconfirmed. Power and energy cannot always be derived exactly from each other. Local daily totals are intended to be calculated from fully validated UTC quarter-hour intervals; API daily aggregates remain excluded while the calendar discrepancies are unresolved. The limited local alpha implements five national power sensors; full implementation and release remain open. See the [contract investigation](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/blob/main/docs/API_REFERENCE.md).

## Priority sensors

The first eight priority national sensors are CO₂ intensity, forecast CO₂ intensity, renewable electricity generation share, solar, onshore wind, offshore wind, total electricity consumption and total electricity generation. The five power sensors are implemented in the alpha; CO₂, forecasts and renewable share remain planned. Renewable share will be explicitly labelled as an estimate based on solar, wind, biomass cofiring and 53% of waste electricity (provisional 2025 CBS annual factor); other mixed sources are excluded. The six input datasets require contract and combined validation first; BL-003 remains open.

## Further information

- [English project documentation](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/blob/main/README.en.md)
- [Changelog](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/blob/main/CHANGELOG.md)
- [Report an issue](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/issues)
- [NED API documentation](https://ned.nl/nl/api)
- [Home Assistant](https://www.home-assistant.io/)
