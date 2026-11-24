# NED API — contractonderzoek

Peildatum: 24 november 2026. Status: openbare documentatie en machineleesbaar schema gecontroleerd; eerste geauthenticeerde waarnemingen geslaagd; volledige contractvalidatie blijft open (BL-003).

## Primaire bronnen

- [API-overzicht](https://ned.nl/nl/api)
- [Handleiding](https://ned.nl/nl/handleiding-api)
- [Productiedatacatalogus](https://ned.nl/datacatalogus)
- [API-changelog](https://ned.nl/nl/changelog-api), nieuwste aangetroffen versie v1.28.0 (19 november 2026)
- [Swagger](https://api.ned.nl/v1), [JSON OpenAPI](https://api.ned.nl/v1/index.jsonopenapi), [YAML OpenAPI](https://api.ned.nl/v1/index.yamlopenapi)

Gebruik de productiebronnen; de acceptatieomgeving kan achterlopen. Documentatiebewijs is geen bewijs van geauthenticeerd runtimegedrag.

## Gedocumenteerd transport en parameters

| Onderdeel | Waarde |
| --- | --- |
| Methode / endpoint | GET https://api.ned.nl/v1/utilizations |
| Authenticatie | Header X-AUTH-TOKEN per verzoek |
| Accept | application/ld+json |
| Gedocumenteerde limiet | 200 verzoeken / 5 minuten |
| Classificatie | 1 forecast, 2 current |
| Granulariteit | 3/4/5/6/7/8 = 10 min / 15 min / uur / dag / maand / jaar |
| Activiteit | 1 opwek, 2 verbruik, 3 import, 4 export, 5 opslag-in, 6 opslag-uit, 7 opslag |
| Point | 0 NL; 1–12 provincies |
| Datumfilters | validfrom[after], validfrom[strictly_before] (ook before en strictly_after gedocumenteerd) |

Querydimensies: point, type, granularity, granularitytimezone, classification, activity en datumfilters. Begin met één dataset per verzoek; collectiefilters en exacte grenzen nog toetsen.

De handleiding geeft tegenstrijdige tijdzone-informatie in het voorbeeld. De parametertabel en tijdzoneparagraaf vermelden 0 = UTC, 1 = Europe/Amsterdam; dag/maand/jaar vereisen 1. Responstijdstempels zijn volgens de handleiding UTC. Verifieer dit, inclusiviteit en DST met echte responses.

Velden: capacity (gemiddeld kW), volume (kWh), emission (kg), emissionfactor (kg/kWh), percentage (benuttingsgraad), validfrom, validto, lastupdate. De getoonde percentagewaarde lijkt een ratio; bewijs schaal en bereik vóór conversie. Het documentatievoorbeeld is geen geldige volledige JSON-response. Null, afwezigheid en nul niet gelijkstellen zonder contractbewijs.

## P0: productiecatalogus

Alle onderstaande typen zijn gedocumenteerd voor historie, current en forecast; horizon maximaal 7 dagen, geen garantie op volledige dekking.

| Type | Activity | Point | Granulariteit | Betekenis |
| --- | --- | --- | --- | --- |
| 1 | 1 | 0, 1–12 | 3–8 | Wind land |
| 2 | 1 | 0, 1–12 | 3–8 | Zon |
| 51 | 1 | 0 | 3–8 | Wind zee |
| 27 | 1 | 0 | 4–8 | Elektriciteitsproductie en CO₂ |
| 59 | 2 | 0 | 4–8 | Elektriciteitsverbruik |

Begin met point=0, granularity=4; forecast/current afzonderlijk. CO₂-productie-intensiteit gebruikt dezelfde dataset 27 als productiecijfers, niet huishoudelijk verbruik. ID 55 betreft lokale distributiebedrijven, niet uitsluitend huishoudens.

### Relevante wijzigingen

- v1.28.0: offshore type 51 gebruikt het vernieuwde model met curtailment; 22 vervalt 18 december 2026, 17 vervalt 28 januari 2027. Gebruik uitsluitend 51 voor nieuwe offshore-implementatie, nationaal. Geen individuele windparken aanbieden zonder nieuw bewijs.
- v1.23.0: ook productiemix 27 en bijbehorende CO₂-forecast tot zeven dagen.
- v1.24.0: vernieuwd model type 59, activiteit 2.
- v1.27.0–1.27.1: bij bronuitval zijn tijdelijk voorspellingen als actuele waarden aangeboden. Classificatie current is daarom geen garantie op gemeten waarden. Historische herberekeningen vereisen revisieverwerking.

## Machineleesbaar schema — opgehaald

Bron: [OpenAPI-export](https://api.ned.nl/v1/docs.jsonopenapi?spec_version=3), opgehaald op 24 november 2026 via [GitHub Actions-run 45466844487](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45466844487). OpenAPI 3.1.0, info.version 0.1.0 (dit is niet de operationele API-changelogversie), 22 paden, 100234 bytes. SHA-256: 4f2a3c1ff88f326b932ce852dd56feee3e60549957ff1083f806531f6b3bf4e6. De gedownloade ZIP en JSON zijn op hash gecontroleerd en lokaal geparseerd. De openbare export wordt niet in de repository gekopieerd.

De oorspronkelijke index-exportlinks faalden: webtoegang ondersteunt het mediatype niet en lokaal DNS ontbreekt. De twee GitHub-pogingen op index.jsonopenapi leverden geen schema op, bij de tweede alleen resourceNameCollection. De docs-route werkt. De eenmalige workflow voor deze openbare download is verwijderd uit de uiteindelijke wijziging.

### Bevestigd in het schema

- GET /v1/utilizations; globale API-key security scheme in de header X-AUTH-TOKEN.
- JSON-LD-collectieobject met verplichte hydra:member-array; optioneel hydra:totalItems (integer), hydra:view met first/last/previous/next IRI's en hydra:search.
- page integer, default 1; itemsPerPage integer, default 144, schema-minimum 0 en maximum 200. Gebruik begrensde positieve waarden, nooit 0. order[validfrom] asc/desc, default desc. Volg in de uiteindelijke client uitsluitend veilige begrensde next-links.
- Queryfilters voor id, point, type, granularity, granularitytimezone, classification, activity; ook arrayvarianten met [] en de vier validfrom-datumfilters. Datasetdimensies worden als querystrings beschreven; het schema noemt de filters optioneel maar de client begrenst altijd de query.
- De recordreferentie Utilization.jsonld kent geen required-lijst. Vereis semantisch essentiële velden in de client pas op basis van de live bevindingen. Paginering en volledige veldvalidatie blijven open.

| Veld | OpenAPI 3.1-type | Aandachtspunt |
| --- | --- | --- |
| id | string | Handleiding toont integer |
| point, type, activity, classification, granularity, granularitytimezone | IRI-reference string | Valideer verwijzingen en verwachte dimensies |
| capacity, volume | string | Handleiding toont numerieke waarden; live representatie verifiëren |
| percentage | number | Schaal blijft open |
| emission | integer of null | Schema-omschrijving CO2/ton versus handleiding kg; eenheid niet bevestigd |
| emissionfactor | number of null | Handleiding kg/kWh |
| validfrom, validto, lastupdate | date-time string | UTC, inclusiviteit en revisies live toetsen |

De schemaomschrijvingen voor activity, classification en granularity lijken achter te lopen op de productiehandleiding/catalogus. Gebruik geen verouderde beperkingen als feit. Voor deze collectie noemt het schema alleen HTTP 200 en 403; betekenis van 401/403, 429 en Retry-After blijft open. Geen opzettelijke fout- of belastingtests tegen productie.

## Eerste live-waarnemingen — 24 november 2026

De eigenaar heeft de beveiligde environment met secret ingericht en de handmatige workflow gestart. [live-run 45469371205](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45469371205) op main (commit 0601ac0a937e6cbe5020e0757d28ed22697b600f) is geslaagd; de joblogs bevestigen twee HTTP 200-responses met application/ld+json en 96 records per aanvraag. De probe vroeg nationale zonne-energie (type 2, activity 1, point 0, granularity 4, granularitytimezone 0) op voor 22 november (classification 2) en 25 november (classification 1).

| Veld of structuur | Waargenomen in beide collecties |
| --- | --- |
| id, capacity, volume | int; afwijking van OpenAPI string |
| emission, emissionfactor | int; geen null waargenomen |
| percentage | int en float |
| point, type, activity, classification, granularity, granularitytimezone | str |
| validfrom, validto, lastupdate | str |
| Collectie | hydra:member, 96 records |
| hydra:totalItems | int (waarde niet gelogd) |
| Paginering | Metadata aanwezig; geen hydra:next |

Alle vijftien onderzochte velden waren aanwezig in deze twee collecties. Er zijn uitsluitend veldtypen, recordaantallen en booleans gelogd; geen ruwe waarden. De toekomstige parser moet rekening houden met de aangetoonde verschillen tussen schema en runtime. Deze observaties bewijzen geen volledige tijdsdekking, timestampformaat, IRI-inhoud, meeteenheid, percentage-schaal of gedrag bij nullwaarden. Bevestigde toegang voor de twee queries is geen bewijs van toegang tot alle datasets.

## Openstaande verificatie

- [x] OpenAPI-export ophalen, parsen en relevante schema's, filters, responses en security scheme inspecteren; verschillen vastgelegd.
- [x] Eerste geautoriseerde begrensde read-only contractobservatie: nationale zon, current/historie en forecast, status, content-type en veldtypen.
- [ ] Resterende nationale P0-combinaties (wind land/zee, productie/CO₂ en verbruik) voor beide classificaties; controleer tijdsdekking en daadwerkelijke dimensies zonder ruwe waarden te loggen.
- [ ] Bevestig paginering, veilige next-links, lege resultaten en datumbereik/offsets; test dagaggregatie en DST.
- [ ] Bevestig meetsemantiek, null versus nul, percentage-schaal, forecastdekking en revisies.
- [ ] Bevestig authenticatie-/autorisatiefouten, rate-limit-scope en Retry-After indien gedocumenteerd of normaal waargenomen. Geen opzettelijke limietoverschrijding.
- [ ] Leg geschoonde fixtures en concrete verificatieresultaten vast; onderscheid synthetische tests van live bewijs.

## Veilige toegang (BL-004)

De [opt-in workflow](../.github/workflows/api-contract.yaml) en [probe](../scripts/ned_contract_probe.py) zijn voorbereid. De workflow draait uitsluitend handmatig op main met expliciete bevestiging, beperkte leesrechten, een vaste environment ned-contract en een jobtimeout van drie minuten. De secret wordt alleen in de probestap geïnjecteerd. De eigenaar heeft bevestigd dat de beveiligde environment en sleutel zijn ingesteld. Behoud de deploymentbranchbeperking tot main en vereiste reviewers waar beschikbaar. De environmentinstellingen zijn niet onafhankelijk uitleesbaar via de huidige connector; de succesvolle handmatige uitvoering op main bevestigt werkende secret-injectie. Gebruik uitsluitend een environment-secret NED_API_KEY, geen repositorybrede secret. Plaats nooit een key in chat, issues, code of artifacts.

Na merge en instelling: start NED API contract observation via Actions op main en vink confirm_live aan. Hiermee autoriseer je maximaal twee GET-verzoeken voor nationale zon (type 2, activity 1), kwartierdata, UTC, elk één dag: twee dagen geleden (current/historie) en morgen (forecast). Per verzoek page=1, itemsPerPage=100, oplopende tijd; geen vervolgpagina's, redirects of retries, sockettimeout 15 s, responslimiet 2 MiB, vaste TLS-host. Geen account-/gebruikersendpoints, geen logging van headers, URL's, ruwe waarden of bodies. Alleen classificatie, aantallen, bekende veldtypen en pagineringsaanwezigheid worden gelogd. Een lege collectie is onvoldoende recordbewijs, geen authenticatiefout. Een alternatieve member-key wordt als waarneming gerapporteerd, niet als bewijs dat het schema klopt. De probe stopt bij de eerste fout. Een groene run bewijst alleen de twee begrensde observaties, niet het volledige contract of datavalidatie.

De maintenance-probe gebruikt uitsluitend de standaardbibliotheek en is geen productieclient. De zes lokale unittest-tests met gesimuleerd transport zijn geslaagd op Python 3.13.5; eerste Baseline CI-run 45467538518 bevestigt de offline tests en audit. Formatterings- en mock-importbevindingen zijn hersteld; herhaalde CI is geslaagd in [Baseline CI-run 45468321699](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45468321699). De bestaande offline pre-commit-suite voert ze uit. De eerste geauthenticeerde observatie is geslaagd; BL-004 is functioneel afgerond. Volgende live-uitbreidingen vereisen opnieuw expliciete opt-in en een beoordeelde begrensde requestset.

De API-client blijft geblokkeerd totdat het noodzakelijke contract en distributiestrategie zijn gevalideerd. Zie [backlog](BACKLOG.md) en [integratieplan](INTEGRATION_PLAN.md).
