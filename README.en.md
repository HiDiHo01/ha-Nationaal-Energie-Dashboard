# Nationaal Energie Dashboard for Home Assistant

[Nederlands](README.md) | English

**[Project website](https://hidiho01.github.io/ha-Nationaal-Energie-Dashboard/)**

Gain insight into energy data and make informed choices using historical, current and forecast information.

This project develops a custom integration for [Home Assistant](https://www.home-assistant.io/) using the [Nationaal Energie Dashboard (NED)](https://ned.nl/) API. The goal is to make Dutch energy data available to Home Assistant sensors, dashboards and automations.

> **Development status:** phase 1 has partially started with the contract-independent package foundation. BL-003 remains open for contract-dependent functionality. No working integration or installable release is available yet.

The development branch contains a limited local alpha (0.1.0a1): real credential validation, an independent UTC quarter-hour parser and five national power sensors. Use only the exact matching locally built wheel for the test installation; no HACS installation or public release. CO₂, forecast and the estimated renewable share remain reserved until their contract conditions are met. New CI and live installation are not yet confirmed; BL-003 and the general phase gates remain open.

Review remediation R39-01–08: status-first error handling, Retry-After, per-attempt budget, independent dataset availability and receipt timestamp. Use the controlled local launcher for the separate test environment. Native lifecycle and wheel preflight tests must pass on the final commit. No new live probes or release.

## Energy data

According to the source description, the NED API provides the data below. The tested national P0 quarter-hour queries have been validated for structure and coverage; further contract and measurement semantics validation remains pending. Integration support is not implemented yet.

| Data | Description |
| --- | --- |
| Electricity production | Dutch generation, both total and by energy source |
| Solar energy | Current and historical data and forecasts |
| Wind energy | Onshore and offshore wind data and forecasts |
| Gas | Gas supply and forecasts for households and small businesses |
| CO₂ | Emissions and emission factors |
| Historical data | Available from 2016 for selected energy sources |
| Forecasts | Up to one week ahead for selected datasets |

Depending on the dataset, available intervals include 10 minutes, 15 minutes, one hour, one day, one month or one year. The NED manual describes power (kW), interval energy (kWh), CO₂ emissions (kg) and emission factors (kg CO₂/kWh). However, the OpenAPI description specifies tonnes for emissions; the examined type-27 quarter-hour records support kg, but the formal unit remains unconfirmed. Power and energy cannot always be derived exactly from each other. Local daily totals are intended to be calculated from fully validated UTC quarter-hour intervals; API daily aggregates remain excluded while the calendar discrepancies are unresolved. See the [contract investigation](docs/API_REFERENCE.md).

## Planned functionality

The first eight priority national sensors are CO₂ intensity, forecast CO₂ intensity, renewable electricity generation share, solar, onshore wind, offshore wind, total electricity consumption and total electricity generation. These are planned features. Renewable share will be explicitly labelled as an estimate based on solar, wind, biomass cofiring and 53% of waste electricity (provisional 2025 CBS annual factor); other mixed sources are excluded. The six input datasets require contract and combined validation first; BL-003 remains open.

- Configuration through the Home Assistant user interface.
- Selectable energy datasets and sensors.
- Historical, current and forecast energy data where supported by the API.
- Correct units, timezone-aware timestamps and appropriate sensor classifications.
- Energy data for dashboards and automations.
- Listing in the general Home Assistant Marketplace catalog.

## API key

Three manually reported authentication observations reproduce HTTP 200 (valid key), 401 (missing) and 403 (invalid) for the same national solar query. The presumed limited key receives access; permission semantics remain open. The alpha client and Config Flow distinguish 401 from 403 without logging error payloads; local owner testing requires successful CI and the exact wheel.

Access to the NED API requires a personal API key.

1. Create an account at [ned.nl](https://ned.nl/).
2. Open **Mijn account** (My account) and select the **API** tab.
3. Generate an API key.
4. Store it securely for future integration setup.

The intended API base URL is https://api.ned.nl/v1. Never disclose API keys in GitHub issues, commits or diagnostic information.

## Installation and configuration

[Local alpha test (separate Core test environment only)](docs/user/en/alpha-test.md).

**Minimum Home Assistant Core version: 2026.11.3.** Each new integration release targets the latest stable Core release as its minimum. Older releases and prereleases need not be supported. The current baseline is a development target, not a tested runtime compatibility claim.

Home Assistant Marketplace is the intended distribution channel. GPL-3.0-only, an OSI-approved license, has been chosen to meet the [HACS license check](https://www.hacs.xyz/docs/publish/include/#check-license). GitHub license detection is confirmed; actual catalog admission still requires verification. The runtime distribution strategy has been validated using a synthetic wheel; full production installation remains pending. Local testing will take place during development. There is no installable release yet. Officially offered versions may be used in Home Assistant subject to the usage terms.

## Development and quality

The objective is a maintainable integration meeting the applicable [Home Assistant Integration Quality Scale](https://contributors.home-assistant.io/core/quality-scale/) criteria, targeting Platinum. This qualification has not yet been achieved or officially awarded.

Technical principles:

- Python follows the latest stable Home Assistant Core release (currently Python 3.14, minimum 3.14.2, development version 3.14.10).
- Asynchronous API communication reusing the Home Assistant web session.
- Central data coordination and API-aware polling.
- Strict type annotations, input validation and consistent error handling.
- Secure reauthentication, reconfiguration and redacted diagnostics.
- Automated tests, linting, type checking and CI validation.

## Language support

The integration and user guides will support Dutch and English, using Home Assistant's native language selection and English fallback. Actual integration translations will be added during implementation. See the bilingual [changelog](CHANGELOG.md).

## Roadmap

See the [prioritized backlog](docs/BACKLOG.md) for outstanding settings, dependencies and acceptance criteria.

- [x] Establish the repository structure and development guidelines.
- [ ] Implement the NED API client and data models.
- [ ] Implement the configuration flow and data coordinator.
- [ ] Provide sensors and forecasts.
- [ ] Add Dutch and English integration translations, diagnostics and error handling.
- [x] Establish development tooling, pre-commit and baseline CI.
- [ ] Complete substantive integration tests and full quality validation.
- [x] Confirm Marketplace admission requirements and runtime distribution strategy (phase 0; actual catalog admission and installation remain pending).
- [ ] Implement Marketplace compatibility, metadata, branding and installation/update tests.
- [ ] Demonstrate successful HACS and Hassfest validation and applicable Platinum criteria.
- [ ] After authorization, publish a complete GitHub release and submit a catalog PR to hacs/default.
- [ ] Verify catalog listing after acceptance.

## Copyright and usage

**Open source under the [GNU General Public License version 3 only (GPL-3.0-only)](LICENSE).**

Use, modification and distribution, including commercial use, are permitted under the GPL. Distribution is subject to applicable source-code, copyleft and notice obligations. Copyright and third-party rights remain intact. See the [license explanation](USAGE_TERMS.md). No official project release is available yet.

## Support and contributions

Report bugs and feature requests through [GitHub Issues](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/issues). Where applicable, include Home Assistant version, integration version and reproduction steps. Remove personal data and API keys from logs.

## References

- [Nationaal Energie Dashboard](https://ned.nl/)
- [Official NED API documentation, manual and data catalog](https://ned.nl/nl/api)
- [NED API](https://api.ned.nl/v1)
- [Home Assistant](https://www.home-assistant.io/)
- [Home Assistant Integration Quality Scale](https://contributors.home-assistant.io/core/quality-scale/)
- [Home Assistant Marketplace](https://contributors.home-assistant.io/marketplace/)
- [Catalog admission](https://contributors.home-assistant.io/marketplace/guides/catalog/)

## Disclaimer

This is an independent project, not an official integration of Nationaal Energie Dashboard or Home Assistant. Energy data availability, timeliness and accuracy depend on the source and the dataset.
