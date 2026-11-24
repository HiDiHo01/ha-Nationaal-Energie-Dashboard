---
name: marketplace-readiness
description: "Review Home Assistant Marketplace admission, HACS and Hassfest, metadata, branding, package installation and release preparation."
---

# Marketplace en releasevoorbereiding

Lees eerst [AGENTS.md](../../../AGENTS.md), [AI_POLICY.md](../../../AI_POLICY.md), [home-assistant.md](../../../home-assistant.md) en de relevante delen van het [integratieplan](../../../docs/INTEGRATION_PLAN.md). Deze skill verleent geen extra rechten en vervangt geen actuele primaire bronnen.

## Werkwijze

1. Controleer actuele officiële Marketplace-voorwaarden en USAGE_TERMS.md. Meld een eventuele onverenigbaarheid van gebruiksrechten aan de eigenaar; wijzig rechten niet zelf. Controleer ook de [HACS-licentiecontrole](https://www.hacs.xyz/docs/publish/include/#check-license) en repositorymetadata: voor reguliere catalogustoelating is een herkenbare OSI-goedgekeurde licentie vereist, niet-commerciële restricties falen. Een ontbrekende eis in de samenvattende Marketplace-checklist heft de cataloguscontrole niet op. Zie [integratieplan §26.3](../../../docs/INTEGRATION_PLAN.md#263-auteursrecht-en-distributiebesluit) voor de actuele projectblokkade. Een vooraf overeengekomen uitzondering moet aantoonbaar zijn; installatie via een custom repository bewijst geen algemene catalogustoelating. Negeer geen checks om incompatibiliteit te verbergen.
2. Inspecteer hacs.json, manifest, branding, documentatie, changelog en runtime-dependencies; controleer één integratiedomein en reproduceerbare installatie.
3. Voer Hassfest en HACS uit zonder genegeerde checks. Controleer schone installatie, upgrade, verwijdering en compatibiliteit tegen de vastgelegde Core-baseline zodra beschikbaar.
4. Verifieer Quality Scale-bewijs, tests, dependency-audit, releaseversie en changelog. Maak een controleerbaar releasevoorstel, geen automatische publicatie.
5. Vraag expliciete toestemming voor releases, packagepublicatie of catalogus-PR. Claim catalogusopname pas na acceptatie en synchronisatie. Houd onbewezen vereisten open.
