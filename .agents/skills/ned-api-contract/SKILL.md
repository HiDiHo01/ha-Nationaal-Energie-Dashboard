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
6. Hergebruik bestaande geschoonde logobservaties voordat je nieuwe live requests voorbereidt. Gebruik voor numerieke semantiek de [begrensde scope semantics](../../../docs/API_REFERENCE.md#gerichte-kwartiersemantiekprobe-scope-semantics); log uitsluitend categorieaantallen en onderscheid diagnostische hypotheses van contractgaranties. Beoordeel de tellingen ook bij een groene workflow: [SEM-001/SEM-002](../../../docs/API_REFERENCE.md#live-resultaat-scope-semantics--24-november-2026) toont afwijkingen van de gedocumenteerde vermogensrelatie en sterke maar begrensde kg-evidentie. Herhaal geen identieke probe zonder nieuwe hypothese. Expliciete live-autorisatie blijft verplicht.
7. Volg voor kalenderaggregaties het [implementatiebesluit in §15](../../../docs/INTEGRATION_PLAN.md#15-tijdzonebeheer-en-historie): standaard granularity 4 en granularitytimezone 0, begrensde queries voor overlappende UTC-kalenderdagen, onafhankelijke validatie van query- en recordtijdzone en volledige intervaldekking. Valideer datumfilters en meetsemantiek per dataset; geen productiegebruik van upstream-dagaggregaties zolang TZ-002/TZ-003 openstaan. Gebruik energy-data-semantics voor de lokale aggregatie.

## Beperkte fase-1-vrijgave

Volg de expliciete eigenaarsbeslissing in [integratieplan §21.2](../../../docs/INTEGRATION_PLAN.md#212-fase-1--api-client). Contractonafhankelijke packageconfiguratie, exceptions en generiek transport mogen worden ontwikkeld met synthetische tests. Geen NED-specifieke statusmapping, rate-limitregels, datasetsemantiek, parser of live aanvragen zonder de toepasselijke bevestiging en autorisatie. BL-003 blijft open; volledige faseacceptatie blijft geblokkeerd. Maak geen aannames om de scope kunstmatig te verruimen.

### Generieke transportlaag

NedTransport leent een vertrouwde certificaatvaliderende aiohttp-sessie en voert GET uit tegen één gevalideerde HTTPS-origin. Standaard ClientTimeout(total=15.0) en maximaal 2 MiB verzamelde responsebytes; dit zijn configureerbare interne ontwerpwaarden, geen NED-limieten. Absolute paden zonder URL-componenten, geen redirects, ssl=True, geen automatische decompressie; vraag identity-encoding aan en wijs andere Content-Encoding af. Geef status en bytes terug als immutable TransportResponse (body niet in repr), zonder statusmapping, JSON-parsing, credentials of applicatieretries. Cancellation blijft intact; transportfouten krijgen geschoonde exceptions zonder ruwe exceptionketen. De caller blijft eigenaar van de sessie en levert uitsluitend niet-gevoelige queryparameters. De wire- en TLS-werking, compressiecompatibiliteit en API-contract zijn niet live getest.

Test met synthetische async responsecontexten en streamingchunks; controleer vaste HTTPS-origin, requestopties, exacte bytegrens, encoding, statusbehoud, geschoonde errors en cancellation. Claim geen TLS- of live contractbewijs uit mocks. Valideer de echte wheel en dependencyversies in CI; houd BL-003 open.
