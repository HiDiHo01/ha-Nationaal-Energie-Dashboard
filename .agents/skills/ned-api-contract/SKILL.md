---
name: ned-api-contract
description: "Verify NED API specifications, datasets, authentication, response parsing, pagination, retry limits and standalone client changes."
---

# NED API-contract en client

Lees eerst [AGENTS.md](../../../AGENTS.md), [AI_POLICY.md](../../../AI_POLICY.md), [home-assistant.md](../../../home-assistant.md) en de relevante delen van het [integratieplan](../../../docs/INTEGRATION_PLAN.md). Deze skill verleent geen extra rechten en vervangt geen actuele primaire bronnen.

## Werkwijze

1. Raadpleeg de officiële NED API-documentatie, datacatalogus en het integratieplan. Leg endpoint, parameters, units, classificatie, tijdzone, authenticatie, paginering en foutcodes vast met bron en datum.
2. Scheid bevestigde contractfeiten van ontwerpveronderstellingen. Gebruik alleen veilige, expliciet toegestane live tests met geïnjecteerde credentials. Geen keys in logs, fixtures of documentatie.
3. Implementeer transport en parsing los van Home Assistant, met geïnjecteerde aiohttp-sessie, begrensde timeouts, paginering, centrale limiter en cancellation.
4. Test geldige en ongeldige responses, null versus nul, onveilige links, 429, retries en revisies met geschoonde fixtures. Label synthetische fixtures.
5. Actualiseer contractdocumentatie en datasetcatalogus alleen op basis van bewijs. Vraag de eigenaar bij onoplosbare materiële onzekerheid; laat afhankelijke taken open.
6. Hergebruik bestaande geschoonde logobservaties voordat je nieuwe live requests voorbereidt. Gebruik voor numerieke semantiek de [begrensde scope semantics](../../../docs/API_REFERENCE.md#gerichte-kwartiersemantiekprobe-scope-semantics); log uitsluitend categorieaantallen en onderscheid diagnostische hypotheses van contractgaranties. Expliciete live-autorisatie blijft verplicht.
7. Volg voor kalenderaggregaties het [implementatiebesluit in §15](../../../docs/INTEGRATION_PLAN.md#15-tijdzonebeheer-en-historie): standaard granularity 4 en granularitytimezone 0, begrensde queries voor overlappende UTC-kalenderdagen, onafhankelijke validatie van query- en recordtijdzone en volledige intervaldekking. Valideer datumfilters en meetsemantiek per dataset; geen productiegebruik van upstream-dagaggregaties zolang TZ-002/TZ-003 openstaan. Gebruik energy-data-semantics voor de lokale aggregatie.
