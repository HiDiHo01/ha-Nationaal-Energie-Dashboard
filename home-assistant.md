# Home Assistant — technische ontwikkelreferentie

## 1. Status en gezag

Dit levende document geldt voor de ontwikkeling van Nationaal Energie Dashboard. Lees het bij iedere Home Assistant-gerelateerde taak. [AI_POLICY.md](AI_POLICY.md) blijft leidend voor mandaat en veiligheid; [AGENTS.md](AGENTS.md) voor technische projectregels; het [integratieplan](docs/INTEGRATION_PLAN.md) voor architectuur, scope en acceptatiecriteria. Dit document specialiseert die regels voor Home Assistant en wijzigt ze niet.

Initiële referentie: 24 november 2026. De repositorybaseline staat in AGENTS.md §4, hacs.json, .python-version en pyproject.toml; controleer deze samen in plaats van hier een onafhankelijke versiepin te onderhouden. Fase 0 blijft open voor BL-003; fase 1 is gedeeltelijk vrijgegeven voor contractonafhankelijke onderdelen volgens het integratieplan. Onderstaande regels zijn ontwikkelvereisten, geen bewijs van een geïmplementeerde of gecertificeerde integratie.

## 2. Upstreamversies en API-onderzoek

- Gebruik de nieuwste stabiele Core-release bij een nieuwe integratierelease; volg de bijbehorende Python-generatie en exacte ontwikkelpin volgens AGENTS.md. Controleer de [stablefeed](https://version.home-assistant.io/stable.json), officiële release-informatie en de betreffende [Core-tag](https://github.com/home-assistant/core/tags).
- Controleer bij iedere API-wijziging de signatures, returntypes, async-contracten, deprecations en upstream-tests van de vastgelegde Core-versie. Gebruik de actuele officiële documentatie; blogposts of voorbeelden kunnen op een andere versie slaan.
- Leg breaking changes, benodigde migraties en regressietests vast. Introduceer geen next-Python-syntax zolang de productieversie die niet ondersteunt.

## 3. Integratiegrenzen en manifest

- Domain nationaal_energie_dashboard; integratietype service; cloud_polling. Houd de zelfstandige ned_api-client vrij van Home Assistant-imports.
- Maak manifest.json pas met echte metadata en gevalideerde runtime-requirements. Verifieer version, config_flow, integration_type, iot_class, documentation, issue_tracker en relevante overige velden tegen de officiële manifestreferentie. Geen onnodige dependencies.
- Houd installatie reproduceerbaar op een schone Home Assistant-omgeving. De distributiestrategie is gevalideerd met een synthetische wheel op de gelockte baseline (BL-006); GPL-3.0-only en GitHub-herkenning op main zijn bevestigd (BL-005, [integratieplan §26.3](docs/INTEGRATION_PLAN.md#263-auteursrecht-en-distributiebesluit)). Verwar installatie via een custom repository niet met algemene catalogustoelating. Voor de API-library is een exact gepinde PyPI-wheel via manifest requirements gekozen; de [tijdelijke runtime-probe](scripts/check_runtime_distribution.sh) slaagt zonder publicatie in [CI](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45482964831/job/138760699296). Herhaal bij relevante wijzigingen; volledige productie-installatie blijft open.

## 4. Config entries en lifecycle

- Gebruik UI-configuratie met Config Flow; valideer credentials met een begrensd bekend geldig request. Voorkom dubbele entries volgens het projectontwerp; behandel een lege response niet automatisch als een authenticatiefout.
- Bewaar credentials in ConfigEntry.data, instellingen in ConfigEntry.options en runtime-objecten in getypeerde ConfigEntry.runtime_data. Controleer de actuele generieke ConfigEntry-signature.
- Implementeer native reauth en reconfigure zonder bestaande registry-identiteiten te wijzigen. Gebruik passende Options Flow en reload-semantiek.
- Initialiseer gedeelde resources en essentiële coordinators vóór platformsetup. Gebruik async_config_entry_first_refresh en de actuele platform-forwarding API. Ruim resources op bij mislukte setup en succesvolle unload; registreer cleanup-callbacks waar passend.
- Test setup, gedeeltelijke setupfouten, unload/reload, migratie, reauth, reconfigure, duplicates en herstel. Laat geen tasks of listeners achter.

## 5. Async I/O, coordinators en beschikbaarheid

- Injecteer de door Home Assistant beheerde aiohttp-sessie via async_get_clientsession; sluit die niet vanuit de client. Gebruik asynchrone transport- en parsingpaden; offload noodzakelijke blokkerende bewerkingen volgens de Core-richtlijnen.
- Houd HTTP-verkeer buiten entity-properties. Gebruik DataUpdateCoordinator voor gedeelde snapshots, CoordinatorEntity voor updates en beschikbaarheid. Splits actuele data en forecast; historie is begrensd on demand.
- Gebruik always_update=False alleen als snapshotvergelijking alle relevante wijzigingen correct detecteert. Houd per-datasetbeschikbaarheid en staleness correct bij; een succesvolle gedeeltelijke refresh maakt niet alle datasets beschikbaar.
- Deel rate limiter, requestbudget en deduplicatie over setup, coordinators, retries, paginering en actions. Respecteer cancellation en Retry-After; valideer API-limieten vóór gebruik.

## 6. Entities, registry en Energy Dashboard

- Gebruik declaratieve SensorEntityDescription, native_value, native_unit_of_measurement, passende device_class en state_class, has_entity_name en translation_key. Gebruik extra_state_attributes voor kleine, nuttige metadata.
- Behoud stabiele unique IDs volgens het integratieplan. Koppel alleen logische serviceapparaten waar dat zinvol is; respecteer gebruikersnamen en registry-keuzes. Geen dynamische identiteit op basis van credentials of veranderlijke labels.
- Valideer units en meetsemantiek vóór registratie. Vermogen en intervalenergie zijn verschillende grootheden; cumulatieve state classes zijn uitsluitend voor semantisch geschikte data. Forecasts zijn geen actuele statistieken. Nationale data is geen huishoudelijke energiemeting.
- Houd tijdstempels timezone-aware, intern UTC; gebruik Europe/Amsterdam voor kalendergrenzen. Test DST, ontbrekende waarden, revisies en onvolledige dekking. Claim Energy Dashboard-compatibiliteit alleen na semantische en technische verificatie.

## 7. Actions, diagnostics, repairs en vertalingen

- Registreer actions volgens het actuele Core-contract in async_setup; gebruik SupportsResponse.ONLY waar passend. Valideer entryselectie, datumbereik, datasetcombinaties en responsegrootte. Geen grote tijdreeksen in Recorder-attributen.
- Vertaal tijdelijke setupfouten naar ConfigEntryNotReady, bevestigde authenticatiefouten naar ConfigEntryAuthFailed, updatefouten naar UpdateFailed en actionfouten naar passende native exceptions. Controleer actuele signatures; preserveer cancellation.
- Diagnostics gebruiken alleen relevante reeds beschikbare data en redacten secrets recursief. Geen extra API-call en geen ruwe gevoelige response. Repairs alleen voor concrete, oplosbare problemen.
- Nederlands en Engels zijn gelijkwaardige verplichte gebruikerstalen. Volg de native taalkeuze van Home Assistant; Engels is de native fallback. Gebruik voor deze custom integratie complete translations/en.json en translations/nl.json met identieke sleutelstructuur en placeholdernamen/-aantallen. Geen strings.json, Core-vertaalreferenties of lege placeholderbestanden. Gebruik native translation keys voor flows, entities, actions, fouten en repairs; technische identifiers en interne code/logging blijven Engelstalig. Valideer bij iedere functionele wijziging de vertalingen en beide gebruikersdocumentatieversies.
- Bevestigd op 24 november 2026 voor Core 2026.11.3: de [custom-integration-vertaalreferentie](https://contributors.home-assistant.io/core/integrations/translations/) en [Core translation.py](https://github.com/home-assistant/core/blob/2026.11.3/homeassistant/helpers/translation.py) beschrijven het laden van translations/<language>.json en de Engelse fallback. Gebruik geen Core-compileproces of niet-opgeloste Core-referenties. Test native taalgedrag en gebruikte keys zodra de integratie bestaat.

## 8. Tests en Platinum

- Volg AGENTS.md en de centrale tooling. Test de zelfstandige client apart van Home Assistant; gewone CI gebruikt mocks, geen live NED-credentials.
- Bewaak strict typing, async library, sessie-injectie en alle toepasselijke lagere Quality Scale-criteria. Gebruik de officiële criterialijst en actuele quality_scale.yaml-syntaxis.
- Onderbouw elke status met code, tests, documentatie of een geldige uitzondering. De interne coveragegrenzen zijn projectvereisten en niet gelijk aan alle officiële drempels.
- Voer Hassfest en Marketplace-validatie zonder genegeerde checks uit zodra prerequisites aanwezig zijn. Een groene workflow met overgeslagen validatie bewijst niets over integratiekwaliteit. Publicatie vereist toestemming.

## 9. Primaire referenties

De onderstaande Home Assistant-documentatiepagina's zijn op 24 november 2026 geopend; controleer voor elke concrete implementatie ook de vastgelegde Core-tag. Andere projectreferenties staan in AGENTS.md.

| Onderwerp | Bron |
| --- | --- |
| Manifest | [Integration manifest](https://contributors.home-assistant.io/core/integrations/manifest/) |
| Config entries | [Config entries](https://contributors.home-assistant.io/core/integrations/config-entries/) |
| Config flow | [Config flow](https://contributors.home-assistant.io/core/integrations/config-flow/) |
| Coordinators | [Fetching data](https://contributors.home-assistant.io/core/integrations/fetching-data/) |
| Sensorsemantiek | [Sensor entity](https://contributors.home-assistant.io/core/entities/sensor/) |
| Async veiligheid | [Blocking operations](https://contributors.home-assistant.io/core/internals/blocking-operations/) |
| Quality Scale | [Integration quality scale](https://contributors.home-assistant.io/core/quality-scale/) |

## 10. Zelfstandig onderhoud

AI controleert dit document bij iedere relevante taak, faseovergang, Core-upgrade en nieuwe deprecation. Verwerk bewezen wijzigingen met bron, datum, toepasselijke versie en impact; verwijder verouderde aanwijzingen. Houd AGENTS.md, integratieplan, skills en tooling consistent. Verander geen mandaat of kwaliteitsdrempel. Meld onopgeloste conflicten en onbevestigde compatibiliteit. Gebruik de [skill-index](.agents/skills/README.md) en de skill project-knowledge-maintenance om herbruikbare kennis vast te leggen.

### Onderhoudslog

- 2026-11-24: NL/EN-beleid en custom-integration-vertaalstructuur gecontroleerd tegen Core 2026.11.3; documentatievalidator voorbereid. Runtimevertaaltests blijven open.

- 2026-11-24: initiële technische referentie aangemaakt op basis van bestaande projectregels en gecontroleerde officiële referentielinks. Geen runtimevalidatie uitgevoerd; fase 0 blijft open.
