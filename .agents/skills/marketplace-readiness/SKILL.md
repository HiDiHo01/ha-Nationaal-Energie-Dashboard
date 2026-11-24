---
name: marketplace-readiness
description: "Review Home Assistant Marketplace admission, HACS and Hassfest, metadata, branding, package installation and release preparation."
---

# Marketplace en releasevoorbereiding

Lees eerst [AGENTS.md](../../../AGENTS.md), [AI_POLICY.md](../../../AI_POLICY.md), [home-assistant.md](../../../home-assistant.md) en de relevante delen van het [integratieplan](../../../docs/INTEGRATION_PLAN.md). Deze skill verleent geen extra rechten en vervangt geen actuele primaire bronnen.

## Werkwijze

1. Controleer actuele officiële Marketplace-voorwaarden en USAGE_TERMS.md. Meld een eventuele onverenigbaarheid van gebruiksrechten aan de eigenaar; wijzig rechten niet zelf. Controleer ook de [HACS-licentiecontrole](https://www.hacs.xyz/docs/publish/include/#check-license) en repositorymetadata: voor reguliere catalogustoelating is een herkenbare OSI-goedgekeurde licentie vereist, niet-commerciële restricties falen. Een ontbrekende eis in de samenvattende Marketplace-checklist heft de cataloguscontrole niet op. Zie [integratieplan §26.3](../../../docs/INTEGRATION_PLAN.md#263-auteursrecht-en-distributiebesluit) voor de gekozen GPL-3.0-only-licentie. Controleer het ongewijzigde LICENSE-bestand, SPDX-metadata en GitHub-herkenning op main; BL-005 is voor dit project bevestigd op main via PR #18; hercontroleer bij wijzigingen. Controleer country NL voor de Nederlandse scope. Een vooraf overeengekomen uitzondering moet aantoonbaar zijn; installatie via een custom repository bewijst geen algemene catalogustoelating. Negeer geen checks om incompatibiliteit te verbergen.
2. Inspecteer hacs.json, manifest, branding, documentatie, changelog en runtime-dependencies; controleer één integratiedomein en reproduceerbare installatie. Gebruik voor BL-006 een tijdelijke wheelhouse en de echte Core requirements-manager op de gelockte baseline; zie [probe](../../../scripts/check_runtime_distribution.sh). Geen editable install, PYTHONPATH, Git-checkout of publieke packagepublicatie als bewijs van de eindgebruikersroute. Onderscheid een synthetische wheelproef van volledige integratie- en releasevalidatie.
3. Voer Hassfest en HACS uit zonder genegeerde checks. Controleer schone installatie, upgrade, verwijdering en compatibiliteit tegen de vastgelegde Core-baseline zodra beschikbaar.
4. Verifieer Quality Scale-bewijs, tests, dependency-audit, releaseversie en changelog. Maak een controleerbaar releasevoorstel, geen automatische publicatie.
5. Vraag expliciete toestemming voor releases, packagepublicatie of catalogus-PR. Claim catalogusopname pas na acceptatie en synchronisatie. Houd onbewezen vereisten open.

### Werkelijke wheel via native requirements (fase 1)

De bestaande native runtimeproef bouwt naast de synthetische wheel ook de werkelijke ned-api-wheel, met de versie uit het package-manifest. Beide worden via async_process_requirements in dezelfde tijdelijke gelockte Core-venv geïnstalleerd vanuit de tijdelijke wheelhouse. Alleen de bouw- en baseline-installatiestap mogen dependencies ophalen; de native requirements-installatie blijft UV_NO_INDEX=1, UV_OFFLINE=1 en UV_NO_CACHE=1. Geen checkout-import, PYTHONPATH, productiecredentials of publicatie. Controleer afwezigheid vooraf, exacte versie, geïsoleerde import, GPL-metadata/licentiebestand, py.typed, exceptionexports, constructie van NedTransport met een geleende aiohttp-sessie zonder request, alle bestaande distributieversies ongewijzigd, uitsluitend beide verwachte nieuwe distributies en uv pip check. Behoud de bestaande zelfstandige wheelcontrole zonder Home Assistant en synthetische proef. Bash-syntaxis, beide ingesloten Python-blokken en TOML lokaal gecontroleerd op Python 3.13.5; uitvoering van de echte native installer op 3.14.10/Core 2026.11.3 wacht op CI. Geen volledige integratieload, HACS-installatie, upgrade, verwijdering of publieke PyPI-resolutie aangetoond.
