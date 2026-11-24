# AGENTS.md — Nationaal Energie Dashboard

## 1. Doel, toepassingsgebied en instructiehiërarchie

Deze instructies gelden voor de volledige repository en alle menselijke en AI-ondersteunde ontwikkelwerkzaamheden.

Ontwikkel de Home Assistant-integratie volgens [docs/INTEGRATION_PLAN.md](docs/INTEGRATION_PLAN.md) (initiële ontwerpversie 1.0.0). Dit integratieplan is de verplichte technische referentie voor scope, architectuur, API-contract, implementatiefasen, risico's, tests en acceptatiecriteria. Lees het relevante hoofdstuk vóór iedere wijziging. Dit bestand vertaalt het plan naar uitvoerbare ontwikkelregels; het plan blijft de bron voor uitgebreide ontwerpdetails.

- Respecteer hogere systeem- en gebruikersinstructies en alle toepasselijke repositoryregels.
- [AI_POLICY.md](AI_POLICY.md) is leidend voor het repositorybeleid zodra het bestand aanwezig is. AGENTS.md is leidend voor technische ontwikkelstandaarden en uitvoering.
- Lees vóór werkzaamheden alle toepasselijke AGENTS.md- en AI_POLICY.md-bestanden in bovenliggende en relevante onderliggende mappen. Specifieke submapregels gelden binnen hun toepassingsgebied; meld conflicten en los ze niet stilzwijgend op.
- Ontbrekende of ontoegankelijke instructies worden expliciet gemeld. Verzin geen beleid en beweer nooit bestanden te hebben gelezen of controles te hebben uitgevoerd als dat niet is gebeurd.
- Inspecteer de actuele branch, werkboom, repositorystructuur, bestaande implementatie, tests en configuratie vóór aanpassingen. Behoud wijzigingen van anderen.
- Volg de vastgelegde architectuur en fasevolgorde. Wijzig fundamentele ontwerpbeslissingen niet stilzwijgend; onderbouw afwijkingen en actualiseer het integratieplan na akkoord.
- De API-aannames in het plan zijn geen bewezen contract. Bij strijdigheid met geverifieerde officiële specificaties: meld de afwijking, corrigeer de ontwerpdocumentatie en implementeer uitsluitend het bevestigde gedrag.
- Voer uitsluitend werkzaamheden uit binnen de opdracht. Geen ongevraagde releases, wijziging van repository-instellingen, destructieve Git-acties of publicatie van dependencies.

### 1.1 Verplicht gebruik en zelfstandig onderhoud van skills

**AI gebruikt relevante skills actief en onderhoudt de projectkennis zelfstandig.** Lees bij aanvang van iedere ontwikkeltaak [home-assistant.md](home-assistant.md) voor Home Assistant-specifieke werkzaamheden en inventariseer de [repositoryskills](.agents/skills/README.md) en andere beschikbare, toegestane skills. Selecteer alle toepasselijke skills op basis van hun beschrijving, lees hun instructies vóór gebruik en volg de relevante procedures. Als automatische skill-discovery niet beschikbaar is, lees de SKILL.md-bestanden rechtstreeks. Meld ontbrekende of ontoegankelijke skills.

- **Automatische skillactivatie is de standaard.** Gebruik native impliciete activatie wanneer de agentomgeving dit ondersteunt. Houd voor alle repositoryskills de metadata agents/openai.yaml met policy.allow_implicit_invocation: true aan; behoud duidelijke triggerbeschrijvingen voor Nederlandse en Engelse opdrachten. Selecteer zo nodig aanvullende relevante skills zelf. Als native discovery of activatie ontbreekt, inventariseer de skill-index en lees de relevante SKILL.md-bestanden rechtstreeks zonder de gebruiker om een skillnaam te vragen. Noem deze methode directe selectie, niet bewezen native activatie.
- Leg de werkelijk gebruikte skills en activatiemethode vast in het opleverrapport. Onderhoud [activatie-evaluaties](.agents/skills/ACTIVATION_EVALS.md) met positieve en negatieve scenario's. Valideer metadata bij wijzigingen; toets native gedrag in een beschikbare geschikte agentomgeving en laat onbewezen evaluaties open.
- **Native gedragsevaluaties zijn een verplichte kwaliteitscontrole voor skills.** Voer de relevante scenario's uit bij nieuwe of inhoudelijk gewijzigde skills, wijzigingen in activatiemetadata, een relevante agent/model-upgrade en vóór de Platinum-acceptatiepoort. Gebruik de [evaluatieprocedure](.agents/skills/ACTIVATION_EVALS.md) en de geïsoleerde runner. Beoordeel tracebewijs, proceduretrouw, uitkomst, onnodige activatie en beleidsnaleving; een statische controle of exitcode is geen bewijs van geslaagd gedrag. Draai niet onnodig alle scenario's bij iedere commit. Gebruik uitsluitend een toegestane, geauthenticeerde evaluatieomgeving zonder productiecredentials; introduceer geen betaalde diensten zonder toestemming. Meld ontbrekende toegang of native trace als blokkade en laat de evaluatiestatus open.
- Gebruik skills voor herhaalbare werkzaamheden zoals API-contractvalidatie, Home Assistant-implementatie, energiedatasemantiek, kwaliteitscontrole, CI/CD, Marketplace en kennisbeheer.
- Beoordeel bij iedere taak en faseovergang welke bewezen nieuwe kennis, regressies, deprecations en werkwijzen herbruikbaar zijn. Actualiseer home-assistant.md en relevante skills zelfstandig wanneer dit aantoonbare waarde heeft. Maak nieuwe skills bij concrete terugkerende taken; voorkom duplicatie en overmatige context.
- Bewaar repositoryskills onder .agents/skills/<skill-name>/SKILL.md met geldige YAML-frontmatter (name en description), gerichte instructies en alleen noodzakelijke referenties, scripts of templates. Onderhoud de index; valideer namen, links en eventuele scripts. Gebruik de skill project-knowledge-maintenance voor dit onderhoud.
- Controleer actuele primaire bronnen en de vastgelegde Home Assistant Core-tag. Noteer bron, datum, versie en onzekerheid bij relevante technische wijzigingen. Geen onbewezen API-feiten, credentials of gevoelige gegevens in skills.
- AGENTS.md en AI_POLICY.md blijven leidend; home-assistant.md specialiseert de technische regels en skills operationaliseren deze. Skills mogen geen beleid versoepelen, extra rechten toekennen of ongeautoriseerde acties starten. Externe skills alleen na controle van herkomst, inhoud en toepasselijkheid; geen automatische installatie zonder vereiste toestemming.
- Rapporteer welke skills relevant zijn gebruikt, welke kennis is bijgewerkt en welke validatie daadwerkelijk is uitgevoerd. Test skillgedrag waar haalbaar; claim geen automatische activatie zonder bewijs.

## 2. Verplichte referenties

| Bron | Referentie |
| --- | --- |
| Integratieplan | [docs/INTEGRATION_PLAN.md](docs/INTEGRATION_PLAN.md) |
| Home Assistant-ontwikkelreferentie | [home-assistant.md](home-assistant.md) |
| Repositoryskills | [.agents/skills/README.md](.agents/skills/README.md) |
| NED API | [Officiële API-documentatie](https://ned.nl/nl/api) |
| NED API-handleiding | [Handleiding](https://ned.nl/nl/handleiding-api) |
| NED OpenAPI | [Swagger](https://api.ned.nl/v1) |
| Home Assistant | [Developer documentation](https://developers.home-assistant.io/) |
| Quality Scale | [Integration Quality Scale](https://contributors.home-assistant.io/core/quality-scale/) |
| Data updates | [Fetching data](https://developers.home-assistant.io/docs/integration_fetching_data/) |
| HACS | [Documentatie](https://www.hacs.xyz/) |
| Python | [Officiële Python-documentatie](https://docs.python.org/) |

Controleer actuele primaire documentatie wanneer API's, dependencies, compatibiliteit, kwaliteitscriteria of gedrag wijzigen. Gebruik geen verouderde voorbeelden als vervanging voor het actuele contract.

## 3. Implementatiefasen en voortgang

Volg hoofdstukken 21 en 22 van het integratieplan. Werk per afgebakend onderdeel; begin niet met afhankelijke functionaliteit voordat de noodzakelijke fundamenten aantoonbaar gereed zijn.

| Fase | Verplichte oplevering | Acceptatiepoort |
| --- | --- | --- |
| 0 — Foundation | AGENTS.md, AI_POLICY.md, auteursrechtbeleid (beperkte gebruikstoestemming), repositorystructuur, pyproject.toml, tooling, basis-CI, gevalideerd API-contract en minimale HA-versie | Beleid, contract en tooling aantoonbaar gereed |
| 1 — API-client | Zelfstandig async ned_api-package, enums, catalogus, modellen, parser, rate limiter, fixtures | Clienttests en contractvalidatie geslaagd |
| 2 — Integration Core | Manifest, config/ options/ reauth/ reconfigure flows, typed runtime data, coordinators, lifecycle en migraties | Setup, reload, unload en flowtests geslaagd |
| 3 — Sensors | P0-datasets, declaratieve entities, device registry, unique IDs, eenheden, vertalingen | Sensortests en semantische datavalidatie geslaagd |
| 4 — Forecast en historie | Forecastsamenvattingen, begrensde response actions, optimale tijdvensters, documentatie | Dekking, DST, revisies en algoritmen getest |
| 5 — Robustness | Diagnostics, relevante repairs, gedeeltelijke uitval, staleness, logging, beveiliging | Fout- en securitytests geslaagd |
| 6 — Platinum | Alle toepasselijke Bronze/Silver/Gold/Platinum-criteria, strict typing, CI en kwaliteitsbestand | Alle toepasselijke releaseblokkades opgelost |
| 7 — Release en Marketplace | Installeerbare build, branding, metadata, installatie/upgrade/verwijdering, changelog en catalogusaanmelding | Gevalideerde release, actuele catalogusvoorwaarden en expliciete publicatietoestemming |

- Gebruik de volledige checklists in hoofdstuk 21 en de Definition of Done in hoofdstuk 24 als acceptatiecriteria.
- Onderhoud de geprioriteerde [backlog](docs/BACKLOG.md) zelfstandig. Werk binnen de opdracht aan uitvoerbare items, respecteer afhankelijkheden en toestemmingseisen, synchroniseer de status met het integratieplan en sluit items alleen met aantoonbaar acceptatiebewijs.
- Werk voortgang bij in het integratieplan en relevante README-roadmap zodra een taak aantoonbaar is voltooid. Laat niet-geteste onderdelen open staan.
- Maak onderscheid tussen geïmplementeerd, getest, geblokkeerd en gepland. Een document of placeholder is geen werkende implementatie.
- Volg Semantic Versioning voor integratie en API-library; versiemijlpalen staan in hoofdstuk 22.
- P0 is de initiële release-scope; breid uit naar P1/P2 volgens het plan en na bevestiging van datasetondersteuning.

## 4. Architectuur en repositorystructuur

| Eigenschap | Ontwerpbaseline |
| --- | --- |
| Domain | `nationaal_energie_dashboard` |
| Integration type | `service` |
| IoT class | `cloud_polling` |
| Python | Volgt nieuwste stable Core; momenteel 3.14 (minimum 3.14.2, ontwikkelpin 3.14.10) |
| Minimale Home Assistant Core-versie | 2026.11.3 (nieuwste stable op 24 november 2026) |
| Transport | aiohttp, HTTPS, gedeelde sessie |
| Configuratie | Native config entry en UI-flows |
| Data | DataUpdateCoordinator, getypeerde immutable snapshots |
| Distributie | Home Assistant Marketplace (publieke catalogus als einddoel) |
| Kwaliteitsdoel | Home Assistant Platinum |

Volg de directorystructuur en moduleverantwoordelijkheden in hoofdstuk 5. Gebruik `custom_components/nationaal_energie_dashboard/` voor Home Assistant-code en `packages/ned-api/src/ned_api/` voor de zelfstandige API-client. Tests worden georganiseerd onder `tests/api/`, `tests/integration/` en `tests/fixtures/`. Ontwerpdocumentatie staat onder `docs/`.

- Scheid transport, parsing, domeinlogica, coordinators, entities en actions. Pas SRP, dependency injection en composition toe.
- De API-library is onafhankelijk van Home Assistant. Bouw en test de library onafhankelijk; valideer in fase 0 een reproduceerbare Marketplace-compatibele runtime-installatiemethode. Publieke packagepublicatie vereist expliciete toestemming.
- Gebruik één centrale datasetcatalogus en één bron voor constanten en enums. Geen verspreide magic numbers of dubbele requestlogica.
- Introduceer modules pas bij concrete verantwoordelijkheid; geen lege placeholders, circulaire imports of speculatieve abstracties.
- Leg afwijkingen van de ontwerpbaseline vast met motivatie, impact en migratiepad.

### 4.1 Home Assistant-versiebeleid

De minimale ondersteunde Home Assistant Core-versie is bij iedere nieuwe integratierelease de dan nieuwste stabiele Core-release, inclusief patchnummer. Controleer deze via https://version.home-assistant.io/stable.json en de officiële release-informatie. Gebruik een expliciete versie per release in hacs.json (homeassistant), documentatie en de reproduceerbare testomgeving; verhoog de grens pas voor een nieuwe integratierelease, niet met terugwerkende kracht. Oudere Core-versies, beta's en developmentversies hoeven niet ondersteund te worden. Valideer vóór publicatie installatie en tests tegen de vastgelegde baseline.

### 4.2 Python-versiebeleid

De Python-doelversie volgt de major.minor-versie die de nieuwste stabiele Home Assistant Core-release gebruikt. Controleer bij het vaststellen van de Core-baseline de officiële release-tag: pyproject.toml (requires-python en toolversies) en .python-version (exacte ontwikkelversie). Neem de officiële minimale Python-versie over en pin de ontwikkelomgeving op de bijbehorende exacte Python-versie. Gebruik dezelfde major.minor-versie voor Ruff, Pylint, mypy en CI. Herbeoordeel deze waarden bij elke nieuwe integratierelease; pas oudere releases niet met terugwerkende kracht aan. Kies nooit zelfstandig een nieuwere Python-generatie dan de vastgelegde Core-baseline.

Baseline 24 november 2026: Home Assistant Core 2026.11.3, Python 3.14, upstream requires-python >=3.14.2 en ontwikkelversie 3.14.10. Bronnen: [Core pyproject.toml](https://github.com/home-assistant/core/blob/2026.11.3/pyproject.toml) en [Core .python-version](https://github.com/home-assistant/core/blob/2026.11.3/.python-version).

## 5. Python-programmeerstandaarden

- Gebruik moderne Python-syntaxis passend bij de volgens paragraaf 4.2 vastgelegde Home Assistant-baseline.
- Volg PEP 8, PEP 257 en de vastgestelde Ruff-, Pylint- en mypy-configuratie. Gebruik twee lege regels vóór top-level functies en klassen; gebruik de gebruikelijke PEP 8-afstand binnen klassen.
- Voeg betekenisvolle docstrings toe aan modules, klassen, functies en methoden, ook interne methoden. Beschrijf contract, parameters, returnwaarde en uitzonderingen waar niet vanzelfsprekend.
- Gebruik volledige typeannotaties voor parameters, attributen waar nodig en returnwaarden. Controleer dat de werkelijke returntypes overeenkomen. Vermijd ongefundeerd Any, casts en brede type-ignore-directives.
- Gebruik ingebouwde generics `list[T]`, `dict[K, V]`, `tuple[T, ...]`, `set[T]` en unions met `|`. Importeer geen List of Dict uit typing.
- Gebruik snake_case voor functies, methoden en variabelen; PascalCase voor klassen; UPPER_CASE voor constanten. Interne methoden hebben een underscore-prefix.
- Hergebruik geen parameternamen als lokale variabelen en overschaduw geen namen uit een buitenliggende scope of built-ins.
- Gebruik waar passend frozen=True, slots=True en kw_only=True voor dataclasses. Plaats velden zonder standaardwaarde vóór velden met standaardwaarde.
- Gebruik canonieke Python-decorators zonder afwijkende formattering; laat Ruff de stijl bewaken.
- Valideer externe invoer en API-responses aan de grens. Geef specifieke, begrijpelijke foutmeldingen zonder gevoelige gegevens.
- Vang specifieke uitzonderingen, behoud de oorzaak met raise ... from exc waar toepasselijk en laat cancellation door. Vermijd bare except en het stilzwijgend onderdrukken van fouten.
- Gebruik lazy %-formattering in logging; geen logging-f-strings (Pylint W1203).
- Refactor en optimaliseer gericht, behoud gedrag tenzij de opdracht het wijzigt en voeg regressietests toe. Vermijd unrelated refactors.

## 6. NED API-contract en datakwaliteit

Volg hoofdstukken 2, 3, 6, 7, 12 en 15 van het integratieplan en de actuele broncontrole in [API_REFERENCE.md](docs/API_REFERENCE.md).

- Valideer dataset-ID's, activiteiten, regio's, classificaties, granulariteit, tijdzone-ID's, velden, headers, authenticatie, paginering, querygrenzen en limieten vóór productiegebruik.
- Gedocumenteerd: HTTPS REST API v1 met /utilizations, X-AUTH-TOKEN en JSON-LD. Het machineleesbare schema is opgehaald; zie de vastgelegde verschillen. De eerste geauthenticeerde zonne-energieobservaties zijn geslaagd; respecteer de gedocumenteerde runtimeveldtypen naast het OpenAPI-schema. Volledige live contractvalidatie en semantiek blijven open.
- Gebruik DatasetKey, DatasetDefinition, EnergyRecord, EnergySeries, DatasetSnapshot, CoordinatorData en NedRuntimeData waar passend. Datasetidentificatie omvat type, point, activity, granularity, classification en granularity_timezone.
- Centraliseer validatie en parsing. Onderscheid nul, null, ontbrekende velden en ongeldige waarden. Wijs NaN, oneindige waarden en ongeldige intervallen af; beoordeel negatieve waarden per metriek.
- Sorteer chronologisch, dedupliceer op dataset plus geldigheidsinterval en verwerk revisies zonder dubbeltelling. Behandel lastupdate niet als automatisch bewijs van inhoudelijke wijziging.
- Gebruik een geldig API-volume als primaire energiebron. Bereken energie uit gemiddeld vermogen alleen bij bewezen geschikte semantiek. Converteer kg/kWh naar g/kWh en gebruik bij aggregaties een passende energiegewogen CO₂-intensiteit.
- Houd actuele waarden, historische waarden en voorspellingen strikt gescheiden. Nationale productie is geen huishoudelijk verbruik of lokale PV-productie.
- Bied alleen ondersteunde datasetcombinaties aan; registreer onbekende API-waarden niet als bewezen ondersteuning.
- Gebruik timezone-aware datetimes en `datetime.now(timezone.utc)`, nooit utcnow(). Bewaar intern UTC en gebruik Europe/Amsterdam voor Nederlandse kalenderaggregaties. Test dagen met 92, 96 en 100 kwartieren en het exacte API-tijdzonecontract.

## 7. Asynchrone communicatie en polling

Volg hoofdstukken 7–9 van het integratieplan.

- Gebruik aiohttp en injecteer Home Assistants sessie via async_get_clientsession. Sluit een geleende sessie nooit zelfstandig.
- Geen blokkerende I/O in de event loop en geen HTTP-aanroepen vanuit entity-properties. Gebruik executor-offloading uitsluitend voor noodzakelijke synchrone bewerkingen volgens HA-richtlijnen.
- Eén centrale requestpipeline voor validatie, budget, timeout, HTTP-status, veilige begrensde paginering, parsing en resultaat.
- Gebruik een gedeelde limiter en requestdeduplicatie voor setup, coordinators, actions, retries en pagina's. Respecteer de echte API-limiet en Retry-After.
- Initiële ontwerpwaarden: actuele polling 5 minuten, forecasts 60 minuten, maximaal 3 gelijktijdige requests, intern maximaal 120 requests per 5 minuten. Verifieer de veronderstelde externe limiet van 200 per 5 minuten en de scope daarvan. Gebruik lagere waarden indien vereist.
- Optimaliseer met caching, gedeelde datasets voor meerdere metrics en alleen aantoonbaar ondersteunde batching. Poll ongebruikte datasets niet.
- Gebruik begrensde exponential backoff met jitter voor tijdelijke fouten; geen onbeperkte retries. Annulering en unload stoppen achtergrondwerk.
- Gebruik afzonderlijke current- en forecastcoordinators en een begrensde on-demand historische provider. Gebruik always_update=False alleen bij correcte snapshotvergelijking.
- Isoleer gedeeltelijke datasetuitval; bewaak staleness en geldigheid, respecteer native coordinatorbeschikbaarheid en herstel automatisch. Presenteer oude data niet als actueel.

## 8. Home Assistant-implementatie

Volg hoofdstukken 9–11, 14, 16 en 18 van het integratieplan en actuele Home Assistant-API's.

- Gebruik één config entry voor de dienst met meerdere geselecteerde datasets en regio's. Voorkom duplicaten.
- Config Flow valideert authenticatie met een beperkt bekend geldig request. Een lege response is geen bewijs van ongeldige credentials.
- Sla credentials op in ConfigEntry.data, gebruikersopties in ConfigEntry.options en runtime-objecten in getypeerde ConfigEntry.runtime_data. Gebruik moderne generieke config-entrytypes waar ondersteund.
- Implementeer Options Flow, native reauth en reconfigure. Behoud entity registry en unique IDs bij keywijziging. Test setup, reload, unload en migraties.
- Gebruik async_config_entry_first_refresh() voor essentiële initiële data. Koppel entities via CoordinatorEntity en gebruik declaratieve SensorEntityDescription.
- Gebruik has_entity_name=True, translation keys, passende entity categories, disabled-by-default waar relevant en logische serviceapparaten per geografisch gebied.
- Behoud stabiele unique IDs met datasetdimensies en metriek volgens hoofdstuk 11. Entity-ID's mogen door de gebruiker gewijzigd worden.
- Gebruik correcte device classes, state classes, native units en native_value. Gebruik extra_state_attributes, nooit het verouderde device_state_attributes.
- Sensorproperties retourneren in-memory data en voeren geen I/O uit. Attributen blijven klein; grote tijdreeksen gaan via response actions.
- Registreer actions in async_setup(), met SupportsResponse.ONLY waar passend, invoervalidatie en geldige config-entryselectie. Begrens datumbereik, respons en requests.
- Nederlands en Engels zijn gelijkwaardige verplichte gebruikerstalen. Volg de native taalkeuze van Home Assistant; Engels is de native fallback. Gebruik voor deze custom integratie complete translations/en.json en translations/nl.json met identieke sleutelstructuur en placeholdernamen/-aantallen. Geen strings.json, Core-vertaalreferenties of lege placeholderbestanden. Gebruik native translation keys voor flows, entities, actions, fouten en repairs; technische identifiers en interne code/logging blijven Engelstalig. Valideer bij iedere functionele wijziging de vertalingen en beide gebruikersdocumentatieversies. Volg ook de actuele vereisten voor manifest, icons en HACS-distributie.
- Start reauth alleen bij bevestigde authenticatiefout. Gebruik ConfigEntryNotReady voor tijdelijke setupfouten, ConfigEntryAuthFailed voor authenticatiefouten, UpdateFailed voor mislukte refreshes, ServiceValidationError voor ongeldige action-invoer en HomeAssistantError voor operationele action-fouten.
- Gebruik Repairs uitsluitend voor relevante oplosbare problemen. Valideer sensorsemantiek: intervalenergie is niet zonder meer TOTAL_INCREASING; forecastwaarden zijn geen actuele statistische metingen.

## 9. Forecast en historie

- Volg hoofdstukken 13–15. Gebruik werkelijk ontvangen horizon en datadekking, niet een gegarandeerde vaste horizon.
- Ontwikkel de P0-action get_forecast en later get_history, get_optimal_period en get_datasets volgens de scope.
- Bereken optimale aaneengesloten tijdvensters uitsluitend met geldige toekomstige dekking; bij gelijke score kies het vroegste venster volgens het ontwerp. Houd rekening met intervalduur, gaten, DST, looptijd en energiegewichten.
- Geen onbeperkte historiecache of forecastarrays in Recorder-attributen.
- Verifieer semantische en technische Energy Dashboard-compatibiliteit vóór enige claim. Geen prijsoptimalisatie of apparaatbesturing binnen de huidige scope.

## 10. Security, privacy en diagnostics

- Volg hoofdstukken 16 en 17. HTTPS en TLS-validatie zijn verplicht; geen onveilige redirects of paginalinks naar externe hosts.
- API-keys, headers, accountgegevens en secrets horen niet thuis in URL's, logs, fixtures, commits, issues, exceptions of diagnostics.
- Redigeer gevoelige configuratie en response-informatie recursief. Log geen volledige ongeschoonde HTTP-body's of uitzonderingsberichten.
- Gebruik begrensde timeouts, response- en paginalimieten en invoer- en schema-validatie. Scan dependencies op kwetsbaarheden.
- Bewaar secrets volgens het native config-entrymechanisme; claim geen automatische encryptie op schijf.
- Diagnostics tonen uitsluitend relevante geredigeerde status, versies, datasetkeuze, dekking, updateleeftijd, recordaantallen en limiterstatus; voer hiervoor geen extra API-call uit.
- Gebruik passende loglevels en voorkom logspam bij terugkerende fouten.

## 11. Tests en kwaliteitscontroles

Volg de teststrategie en de volledige scenario-checklist in hoofdstuk 19. Iedere gedragswijziging krijgt passende unit-, integratie- of regressietests. Reguliere CI is deterministisch, zonder live netwerk of echte API-key; opt-in contracttests zijn gescheiden, begrensd en gebruiken veilig geïnjecteerde credentials.

| Onderdeel | Interne streefdekking |
| --- | ---: |
| Config Flow, forecastberekeningen, diagnostics | 100% |
| API-client, parser, modellen, coordinators, sensors, actions | ≥95% |
| Totale branch coverage | ≥95% |

Test authenticatie, netwerkfouten, 429, onveilige paginering, malforme responses, concurrency, cancellation, lifecycle, unieke IDs, gedeeltelijke uitval, revisies, eenheden, DST, onvolledige forecasts en credentialredactie. Deze interne doelen vervangen de officiële toepasselijke kwaliteitscriteria niet.

De root-pyproject.toml is een niet-installeerbare ontwikkelworkspace (uv package=false); de zelfstandige API-library krijgt in fase 1 eigen buildmetadata. Gebruik de officiële pytest-homeassistant-plugin met exact dezelfde versie als Home Assistant Core; installeer niet daarnaast pytest-homeassistant-custom-component. De dev-dependencygroep bevat de tooling. Lock de volledige dependencyboom in fase 0 en valideer de installatie op de exacte .python-version. Gebruik `mypy` zonder padargumenten voor alle in pyproject.toml vastgelegde bron- en testmappen. De coverage-configuratie bewaakt de totale gecombineerde lijn- en branchdekking met branchmeting ingeschakeld (95%); de aanvullende per-module- en afzonderlijke branchdoelen moeten in CI expliciet worden bewaakt. Live API-tests krijgen marker live_api en zijn standaard uitgesloten; voer deze alleen expliciet uit met veilige credentials.

### 11.1 Validatiecommando's

Gebruik de volgende geplande commando's vanuit de repository-root zodra de tooling en bijbehorende modules in fase 0/1 zijn ingericht. Gebruik vervolgens de vastgestelde configuraties in pyproject.toml en CI. Een ontbrekende dependency of module is een blokkade, geen geslaagde controle.

```bash
ruff format --check .
ruff check .
pylint custom_components/nationaal_energie_dashboard
pylint packages/ned-api/src/ned_api
mypy
pytest --cov --cov-branch --cov-report=term-missing
pip-audit
```

- Draai tijdens ontwikkeling gerichte tests en vóór oplevering alle toepasselijke kwaliteitscontroles. Valideer documentatiewijzigingen met beschikbare Markdown-controles en controleer interne verwijzingen.
- Gebruik reproduceerbare dependencyversies en voer HACS-, Hassfest-, security-, packagebuild- en releasevalidatie uit waar van toepassing.
- Rapporteer gebruikte commando's, exitstatussen, testresultaten en niet-uitgevoerde controles. Meld beperkingen, ontbrekende tooling en failures expliciet. Wijzig geen tests of thresholds uitsluitend om een failure te maskeren.

### Forward Compatibility Testing

- De Home Assistant/Python-baseline blijft leidend voor productiecode, linting, strict typing, volledige integratietests en de verplichte coveragepoorten.
- Onderhoud de afzonderlijke workflow python-next-smoke.yaml voor de eerstvolgende Python-major.minor-generatie (momenteel 3.15, productie 3.14). Deze experimentele job is niet releaseblokkerend (continue-on-error: true); failures blijven zichtbaar in de jobdetails. Bij een Core/Python-upgrade schuift de experimentele versie mee. Introduceer geen next-only syntax in productiecode.
- Draai op push, pull request en workflow_dispatch met alleen contents: read, zonder API-secrets of installatie van Home Assistant/het root-dev-dependencygroup.
- Controleer de volgende-versierelatie met .python-version, compileer aanwezige Python-bronnen, installeer de zelfstandige ned_api-library vanuit packages/ned-api, voer pip check en een import uit en draai offline tests/api zonder de root-coveragepoort.
- Voeg in fase 1 een zelfstandige test-extra toe aan packages/ned-api/pyproject.toml (pytest, pytest-asyncio en alle vereiste API-testdependencies, geen Home Assistant). API-tests en fixtures zijn onafhankelijk van Home Assistant; plaats noodzakelijke conftest-fixtures onder tests/api. Sluit live_api-tests uit.
- Zolang broncode of tests ontbreken, rapporteert de workflow expliciet welke controles niet zijn uitgevoerd. Een groene experimentele job is geen bewijs van volledige runtimecompatibiliteit of Platinum.

## 12. Platinum Quality Scale

- Ontwerp vanaf het begin voor alle toepasselijke Bronze-, Silver-, Gold- en Platinum-criteria.
- Controleer de actuele officiële criterialijst en bestandsstructuur; gebruik quality_scale.yaml voor traceerbaarheid.
- Markeer criteria als done, todo of exempt volgens de actuele geldige syntaxis. Koppel bewijs aan done; onderbouw iedere uitzondering. Markeer geen criterium als voltooid op grond van alleen dit plan.
- Platinum vereist onder meer een asynchrone dependency, sessie-injectie en strict typing, naast alle toepasselijke lagere eisen.
- Presenteer Platinum als aantoonbaar intern kwaliteitsdoel, niet als officiële certificering van deze custom integration.

## 13. Git, CI/CD en documentatie

- Werk in kleine, logisch samenhangende wijzigingen. Volg het voorgestelde branchbeleid (feature/*, fix/*, docs/*) voor reguliere ontwikkeling zodra fase 0 dit heeft ingericht. Respecteer de actuele branchbescherming en gebruikersopdracht.
- Gebruik betekenisvolle commitberichten, bij voorkeur Conventional Commits. Verifieer de diff vóór commit; voer geen force-push of destructieve reset uit.
- Richt CI in volgens hoofdstuk 20: Ruff, Pylint, strict mypy, pytest met branch coverage, dependency scanning, Hassfest, HACS en releasevalidatie. Publieke publicatie vereist expliciete toestemming en bevestigde catalogusvoorwaarden.
- Werk relevante README, changelog, architectuur-, API-, dataset-, installatie-, configuratie-, entiteits-, automatiserings-, troubleshooting- en ontwikkelaarsdocumentatie bij.
- Documenteer publieke API-contracten, configuratieopties, eenheden, beperkingen, breaking changes en migratiepaden.
- Houd AGENTS.md voor technische standaarden, AI_POLICY.md voor beleid en INTEGRATION_PLAN.md voor ontwerp en fasevoortgang. Vermijd dubbele of tegenstrijdige bronnen.

### Autonoom documentatie- en taalbeheer

**Verplichte regel: AI beheert documentatie autonoom.** Controleer bij iedere taak en faseovergang de impact op README, changelog, backlog, integratieplan, ontwikkelreferenties, skills en gebruikersdocumentatie. Werk alle geraakte documenten in dezelfde pull request bij zonder afzonderlijke opdracht. Baseer status, voorbeelden, versies en compatibiliteitsclaims op geverifieerde implementatie en testbewijs. Vermeld ontbrekende controles en onderhoud canonieke bronnen zonder duplicatie. Houd beide gebruikersdocumentatietalen inhoudelijk gelijkwaardig; gebruik README.md (NL), README.en.md (EN) en voor nieuwe gebruikershandleidingen gelijknamige bestanden onder docs/user/nl en docs/user/en. Changelog bevat beide talen; interne technische en beleidsdocumenten mogen Nederlands blijven. Verifieer verwijzingen, vertaalpariteit en inhoudelijke juistheid vóór oplevering. Wijzig geen rechten of kwaliteitscriteria.

- Onderhoud de openbare tweetalige projectsite onder site/ bij relevante gebruikersgerichte wijzigingen. Publiceer alleen de expliciete allowlist via [Pages-workflow](.github/workflows/pages.yaml); houd de status gelijk aan de README-versies en link naar de canonieke gebruiksvoorwaarden. Geen interne documenten, secrets of ruwe testgegevens in het publicatiepakket.

- Voer de [documentatievalidator](scripts/check_project_docs.py) en de regressietests via pre-commit uit. Controleer inhoud en externe verwijzingen aanvullend handmatig; bestandspariteit bewijst geen vertaal- of inhoudskwaliteit. Vertalingen zijn verplicht vanaf het manifest, of eerder zodra vertaalbestanden worden toegevoegd. Houd ontbrekende native gedragsevaluaties expliciet open.

### 13.1 Auteursrecht en distributie

- Alle rechten voorbehouden, met beperkte gebruikstoestemming voor Home Assistant volgens [USAGE_TERMS.md](USAGE_TERMS.md). Geen open-sourcelicentie. Verleen geen aanvullende rechten aan derden zonder toestemming.
- Respecteer wettelijke uitzonderingen, GitHub-voorwaarden en licenties van externe materialen.
- Marketplace-distributie van officiële versies is het doel. Publicatie van releases, packages of catalogusaanmelding vereist expliciete toestemming. Wijzig repositoryzichtbaarheid niet zelfstandig.

### 13.2 Marketplace-readiness

- Volg [repositoryvereisten](https://contributors.home-assistant.io/marketplace/reference/repository-structure/) en [catalogusprocedure](https://contributors.home-assistant.io/marketplace/guides/catalog/).
- Bevestig in fase 0 of de beperkte gebruikstoestemming voldoet aan de actuele toelatingsvoorwaarden; vraag de eigenaar bij een vereiste beleidswijziging.
- Eén integratie in custom_components/nationaal_energie_dashboard; root-hacs.json, geldig manifest, branding, README, beschrijving, topics en ingeschakelde issues. Alle runtime-dependencies zijn beschikbaar bij een schone installatie.
- Vereis geslaagde HACS- en Hassfest-validatie zonder genegeerde checks, volledige GitHub-release, installatie-/update-/verwijderingstests en catalogus-PR bij hacs/default (integration).
- Claim catalogusopname pas na acceptatie en synchronisatie. Platinum blijft een afzonderlijk kwaliteitsdoel.

### 13.3 CI-workflows en onderhoud

**Verplichte regel: AI beheert CI/CD proactief en zelfstandig.** Beoordeel bij iedere ontwikkeltaak en faseovergang of nieuwe of verbeterde GitHub Actions-workflows aantoonbare meerwaarde bieden voor kwaliteit, veiligheid, compatibiliteit, reproduceerbaarheid, onderhoud of Marketplace-readiness. Ontwerp, implementeer, test en onderhoud dergelijke workflows binnen het bestaande mandaat van AI_POLICY.md zonder op een afzonderlijke opdracht of routinegoedkeuring te wachten.

- Inspecteer bestaande workflows en recente relevante CI-resultaten; herstel relevante fouten en verouderde configuratie zelfstandig. Hergebruik bestaande controles en voorkom duplicatie, onnodige runs, betaalde verplichtingen en speculatieve workflows.
- Automatiseer toepasselijke kwaliteits-, regressie-, dependency-, security-, build- en compatibiliteitscontroles zodra de noodzakelijke implementatie beschikbaar is. Gebruik waar passend geplande controles en handmatige triggers. Houd workflows synchroon met de actuele Home Assistant/Python-baseline en Platinum-acceptatiecriteria.
- Valideer wijzigingen lokaal waar mogelijk, controleer de werkelijke GitHub Actions-resultaten en documenteer relevante failures, ontbrekende prerequisites en niet-uitgevoerde controles. Houd de roadmap en workflowdocumentatie actueel. Verlaag geen kwaliteitsdrempels en verwar overgeslagen controles niet met geslaagde tests.
- Respecteer minimale rechten, veilige secret-injectie, vastgepinde actions en AI_POLICY.md. Geen automatische publicatie, ongeautoriseerde live API-aanroepen, wijziging van repository-instellingen of betaalde verplichtingen zonder de vereiste toestemming. Experimentele controles blijven duidelijk onderscheiden van verplichte releasepoorten.

- Gebruik de gelockte ontwikkelomgeving en [pre-commit](.pre-commit-config.yaml): `uv sync --locked`, `uv run --locked pre-commit install --install-hooks` en `uv run --locked pre-commit run --all-files`. Baseline CI voert dezelfde hooks uit; geen dubbele Ruff-, Pylint- of mypy-configuratie. Externe hooks zijn op volledige commit-SHA's vastgepind en worden dagelijks via Dependabot gecontroleerd. Wijzigingen aan hookconfiguratie vereisen afzonderlijke beoordeling. Gitleaks scant de Git-index met geredigeerde uitvoer; dit is geen garantie dat alle secrets worden gevonden. De VS Code-configuratie gebruikt de workspace-venv en centrale toolconfiguratie; CI blijft gezaghebbend.
- Baseline CI (ci.yaml) installeert de exacte .python-version, controleert de Core- en toolversies, gebruikt uv 0.13.9 en valideert dependencies. De gecommitteerde uv.lock is verplicht; uv lock --check en uv sync --locked bewaken de reproduceerbaarheid. Geen automatische regeneratie in CI. Voeg de zelfstandige API-library met testdependencies toe aan de gelockte ontwikkelomgeving zodra deze beschikbaar is.
- Baseline CI bewaakt Ruff, Pylint, strict mypy, offline pytest, de gecombineerde coveragepoort, de afzonderlijke totale branchcoverage en de huidige modulecategorieën. Pas de coveragecontrole aan wanneer forecastberekeningen of andere kritieke modules andere bestandsnamen krijgen. Dependency-audit draait met pip-audit; kwetsbaarheden mogen niet stilzwijgend worden onderdrukt.
- Hassfest draait automatisch zodra het manifest aanwezig is; vóór dat moment wordt de ontbrekende validatie expliciet gemeld. Handmatige Hassfest-validatie vereist een manifest. Marketplace-validatie (hacs.yaml) draait handmatig en na een geautoriseerde gepubliceerde release, zonder genegeerde HACS-checks of PR-commentaar. Een echte succesvolle validatie is vereist vóór catalogusaanmelding.
- Baseline-watch controleert dagelijks de officiële Core-stablefeed en meldt afwijkingen zonder automatisch de versiegrens te wijzigen. Controleer bij de volgende release ook het upstream Python-contract. Dependabot controleert dagelijks GitHub Actions en de uv-dependencyboom (directe en indirecte dependencies, inclusief ontwikkeltools). Groepeer minor/patch-updates; beoordeel major-updates afzonderlijk. Home Assistant en pytest-homeassistant blijven gekoppeld aan de vastgelegde Core/Python-baseline en worden gezamenlijk bijgewerkt volgens §4.1–4.2. De ignore-regels gelden ook voor Dependabot-securityupdates van deze twee packages; bewaak hun kwetsbaarheden via pip-audit en upstream-beveiligingsmeldingen en behandel noodzakelijke fixes met voorrang. Houd de uv-installatieversie en andere toolpins buiten de ondersteunde manifesten actief bij; de externe pre-commit-hooks worden dagelijks door Dependabot gecontroleerd; voeg de zelfstandige API-library toe zodra haar manifest bestaat. Controleer iedere dependency-PR op herkomst, changelog, compatibiliteit, lockfile, security en toepasselijke CI. De workflow dependabot-automerge.yaml verwerkt uitsluitend geverifieerde Dependabot-minor/patchupdates voor main: geen checkout of uitvoering van PR-code, metadata en bestandscontrole met leesrechten, afzonderlijke mergejob met minimale schrijfrechten, geslaagde verplichte checks en squash-merge op de gecontroleerde head-SHA zonder bypass. Core/pytest-homeassistant, major/onbekende updates, maintainerwijzigingen, andere bestanden en de mergeworkflow zelf vereisen afzonderlijke beoordeling. Gewone workflowwijzigingen mogen alleen bestaande action-SHA's vervangen. GitHub blijft de ruleset afdwingen. De workflow gebruikt geen PAT en wacht begrensd op CI; bij failure, timeout of gewijzigde SHA wordt niet gemerged. Een GITHUB_TOKEN-merge kan opvolgende push-workflows onderdrukken; verifieer dit bij de eerste echte botmerge. Bewaar BL-017 als in uitvoering totdat echte end-to-end-validatie beschikbaar is.
- Gebruik standaard contents: read, vastgepinde action-SHA's, geen persistente checkoutcredentials en geen secrets in gewone CI. Upstream Hassfest/HACS-actions gebruiken zelf containerimages met veranderlijke tags; de action-SHA alleen maakt hun uitvoering niet volledig reproduceerbaar.
- De experimentele Python-next-job blijft afzonderlijk en niet-blokkerend. Geen automatische releases, packagepublicaties of live contractrequests. De opt-in api-contract.yaml is uitsluitend voor een expliciet geautoriseerde, begrensde contractobservatie op main met een branchbeperkte environment ned-contract en NED_API_KEY. Volg de veiligheidsvoorwaarden in API_REFERENCE.md; geen secrets in reguliere CI. Voeg releasevalidatie toe zodra distributiemethode en buildvereisten concreet beschikbaar zijn.

## 14. Definition of Done en opleverrapport

Een onderdeel is pas gereed wanneer alle toepasselijke punten uit hoofdstuk 24 aantoonbaar zijn afgedekt:

- [ ] AGENTS.md en toepasselijke AI_POLICY.md gevolgd; relevante skills en home-assistant.md gebruikt en waar nodig bijgewerkt.
- [ ] De actuele Python- en Home Assistant-baseline gerespecteerd.
- [ ] Volledige type hints en docstrings.
- [ ] Geen blokkerende I/O of achterblijvende async-taken.
- [ ] Invoer, API-contract en responses gevalideerd.
- [ ] Consistente foutafhandeling en correcte databetekenis.
- [ ] Geen gevoelige gegevens in logging, diagnostiek of repository.
- [ ] Unit- en integratietests geslaagd.
- [ ] Ruff, Pylint en strict mypy geslaagd.
- [ ] Vereiste toepasselijke testdekking behaald.
- [ ] Autonome documentatie-impactanalyse uitgevoerd; geraakte documenten, NL/EN-gebruikersdocumentatie, vertalingen, changelog, backlog en planvoortgang synchroon; documentatievalidator en inhoudelijke review uitgevoerd.
- [ ] Toepasselijke Quality Scale-criteria onderbouwd.
- [ ] Toepasselijke GitHub Actions en releasecontroles geslaagd.
- [ ] Geen openstaande releaseblokkerende fouten.

Rapporteer bij iedere opdracht de gewijzigde bestanden, relevante technische keuzes, afwijkingen van het plan, uitgevoerde controles en exacte resultaten, niet-uitgevoerde controles, blokkades en actuele fase. Geef één onderbouwde oplossing; maak wijzigingen duidelijk herkenbaar.

## 15. Startstatus en volgende acceptatiepoort

Bij het opstellen van dit bestand bevatte de repository alleen README.md en docs/INTEGRATION_PLAN.md. Fase 0 is gestart, niet voltooid. AGENTS.md en AI_POLICY.md zijn aanwezig. De eigenaar heeft gekozen voor beperkte Home Assistant-gebruikstoestemming met voorbehouden overige rechten. De basismappenstructuur is aanwezig; Marketplace-readiness is nog niet aangetoond. De minimale Home Assistant-versie is vastgesteld op 2026.11.3 (nieuwste stable op 24 november 2026). Tooling en basis-CI zijn operationeel. API-contractvalidatie, distributiestrategie en runtimecompatibiliteitstests blijven open.

Werk eerst de openstaande onderdelen van fase 0 af. Implementeer de API-client pas wanneer de noodzakelijke beleids-, contract- en toolingfundamenten gereed zijn. Als een externe afhankelijkheid (zoals een NED API-key) ontbreekt, meld de blokkade en voltooi alleen onafhankelijke werkzaamheden die verantwoord uitvoerbaar zijn.
