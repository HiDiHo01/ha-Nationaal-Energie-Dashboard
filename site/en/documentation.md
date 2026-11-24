---
lang: en
title: Documentation
description: Requirements, development status and support.
permalink: /en/documentation/
other_lang: nl
other_url: /nl/documentation/
---
## Installation and requirements

The integration is still in development. No installable release is available. Distribution through Home Assistant Marketplace is intended. GPL-3.0-only has been chosen to meet the [HACS license requirement](https://www.hacs.xyz/docs/publish/include/#check-license). GitHub license detection is confirmed; actual catalog admission remains pending. The runtime distribution strategy has been validated using a synthetic wheel; full production installation still requires verification.

## NED API key

For future use, create an account at [NED](https://ned.nl/), open Mijn account (My account) → API and generate a personal API key. Store it securely. Never disclose keys in issues or logs.

## API contract status

The tested national P0 quarter-hour queries have been structurally validated. The NED manual describes power (kW), interval energy (kWh), CO₂ emissions (kg) and emission factors (kg CO₂/kWh). However, the OpenAPI description specifies tonnes for emissions; the examined type-27 quarter-hour records support kg, but the formal unit remains unconfirmed. Power and energy cannot always be derived exactly from each other. Local daily totals are intended to be calculated from fully validated UTC quarter-hour intervals; API daily aggregates remain excluded while the calendar discrepancies are unresolved. The integration has not been implemented yet. See the [contract investigation](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/blob/main/docs/API_REFERENCE.md).

## Priority sensors

The first eight priority national sensors are CO₂ intensity, forecast CO₂ intensity, renewable electricity generation share, solar, onshore wind, offshore wind, total electricity consumption and total electricity generation. These are planned features. Renewable share will be explicitly labelled as an estimate based on solar, wind, biomass cofiring and 53% of waste electricity (provisional 2025 CBS annual factor); other mixed sources are excluded. The six input datasets require contract and combined validation first; BL-003 remains open.

## Further information

- [English project documentation](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/blob/main/README.en.md)
- [Changelog](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/blob/main/CHANGELOG.md)
- [Report an issue](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/issues)
- [NED API documentation](https://ned.nl/nl/api)
- [Home Assistant](https://www.home-assistant.io/)
