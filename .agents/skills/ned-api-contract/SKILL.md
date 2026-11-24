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
