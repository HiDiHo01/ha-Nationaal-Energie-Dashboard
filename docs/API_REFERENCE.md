# NED API — contractonderzoek

Peildatum: 25 november 2026. Status: openbare documentatie en machineleesbaar schema gecontroleerd; eerste geauthenticeerde waarnemingen geslaagd; volledige contractvalidatie blijft open (BL-003).

## Primaire bronnen

- [API-overzicht](https://ned.nl/nl/api)
- [Handleiding](https://ned.nl/nl/handleiding-api)
- [Kolom- en datasetdefinities](https://ned.nl/nl/definities)
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

De handleiding geeft tegenstrijdige tijdzone-informatie: 0 = UTC, 1 = Europe/Amsterdam, maar het voorbeeld toont een request met 1 en een record met 0. De handleiding vermeldt dat dag/maand/jaar 1 vereisen. Live-observaties hieronder bevestigen voor nationale historische zonne-energie dat kwartierdata met querytijdzone 1 records met tijdzone-ID 0 en correcte Nederlandse kalendergrenzen levert. Ook levert daggranulariteit met querytijdzone 0 een record op, in strijd met de verwachte beperking. De gerichte dagprobe hieronder heeft beide grensafwijkingen gemeten; oorzaken en meetsemantiek blijven open.

Velden volgens de handleiding: capacity (naar uurwaarde omgerekende capaciteit in kW), volume (intervalenergie in kWh), emission (kg volgens handleiding, ton volgens OpenAPI; formele eenheid onbevestigd, zie SEM-002), emissionfactor (kg/kWh volgens handleiding), percentage (benuttingsgraad), validfrom, validto, lastupdate. De getoonde percentagewaarde lijkt een ratio; bewijs schaal en bereik vóór conversie. Het documentatievoorbeeld is geen geldige volledige JSON-response. Null, afwezigheid en nul niet gelijkstellen zonder contractbewijs.

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

De schemaomschrijvingen voor activity, classification en granularity lijken achter te lopen op de productiehandleiding/catalogus. Gebruik geen verouderde beperkingen als feit. Voor deze collectie noemt het schema alleen HTTP 200 en 403; betekenis van 401/403, 429 en Retry-After blijft open. Geen nieuwe opzettelijke fout- of belastingtests tegen productie; zie de afzonderlijk gerapporteerde handmatige authenticatieobservaties.

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

## Uitgebreide live-observaties — 24 november 2026

[live-run 45474134929](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45474134929/job/138729707092) op main (460f980b8a9ce4de6c45278ba0ff5362ae971e95, PR #13) is gedeeltelijk geslaagd. Alle tien nationale P0-queries voor type 1, 2, 51, 27 en 59, classification 2 (22 november) en 1 (25 november), point 0, granularity 4, granularitytimezone 0 en correcte activity hebben 96 records, correcte IRI-dimensies, UTC-aware tijdstempels, volledige geordende intervaldekking en overeenkomende totalItems. De twee paginaverzoeken voor nationale zon leveren 48 + 48 records, een exact veilige next-link en geen extra pagina, samen dezelfde volledige tijdsdekking.

In deze twaalf responses waren alle vijftien onderzochte velden aanwezig. id, capacity, volume en emission zijn integers; emissionfactor is float voor type 27 en integer voor de andere vier typen. Percentage is int en/of float, zonder waargenomen negatieve waarden of waarden boven één. Voor type 59 is percentage steeds nul; emission en emissionfactor zijn voor de vier andere typen dan 27 steeds nul. Deze observaties bewijzen geen eenheden, ratio-conversie of algemene nullability.

Het dertiende verzoek (nationale zon, 29 maart 2026, granularity 4, granularitytimezone 1) stopt met Unexpected dataset dimension: granularitytimezone. De werkelijke ontvangen IRI en intervaldekking zijn niet bekend. De handleiding toont bij een request met timezone 1 een respons met IRI-ID 0; de tekst beschrijft timezone als interpretatie van het datumfilter. Dit ondersteunt een te onderzoeken onderscheid tussen querytijdzone en recordtijdzone, maar bewijst niet de werkelijke IRI in deze run. Wijzig de acceptatieregels voor productiegegevens niet op grond van deze hypothese.

De vervolgprobe biedt scope timezone (zes requests) of full (18). Alleen bekende timezone-IRI-ID's 0/1 worden als veilige categorieën gerapporteerd; onbekende referenties worden zonder ruwe waarde verworpen. De querytijdzone, waargenomen recordtijdzone-ID's en intervaldekking worden apart beoordeeld. Bij een bekende ID-afwijking of afwijkende geldige totaaltelling op een enkelvoudige pagina gaan de onafhankelijke scenario's door, maar de eindstatus blijft failure. Onveilige links, transport-/schemafouten en foutieve andere dimensies blijven onmiddellijk blokkerend. Een lege collectie levert geen bewijs van een response-timezone-ID. Bij die uitvoering was de standaard scope timezone om reeds bewezen requests niet te herhalen.

## Vervolgobservaties tijdzones — 24 november 2026

[live-run 45475494852](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45475494852/job/138734501798), commit d46e5963602425655001aa2690669f674ce188aa (PR #14), scope timezone: alle zes begrensde aanvragen uitgevoerd; eindstatus failure. Alle aanvragen betreffen historische nationale zonne-energie (type 2, point 0, activity 1, classification 2). De probe valideert UTC-aware begin- en eindtijdstempels, geordende intervaldekking, dimensies en totalItems. Dit zijn geen algemene garanties voor andere datasets of granulariteiten.

| Datum | Granulariteit | Querytijdzone | Response-ID | Records (verwacht / ontvangen) | Exacte dekking |
| --- | --- | --- | --- | --- | --- |
| 2026-03-29 | 4 (kwartier) | 1 | 0 | 92 / 92 | Correct |
| 2026-10-25 | 4 (kwartier) | 1 | 0 | 100 / 100 | Correct |
| 2026-11-22 | 4 (kwartier) | 1 | 0 | 96 / 96 | Correct |
| 2026-03-29 | 6 (dag) | 1 | 1 | 1 / 1 | Correct (23 uur) |
| 2026-10-25 | 6 (dag) | 1 | 1 | 1 / 1 | Afwijkend van verwachte 25-uursintervalgrenzen |
| 2026-11-22 | 6 (dag) | 0 | 0 | 0 / 1 | Niet gevalideerd; de oude verwachting was een lege collectie |

Voor alle zes responses zijn de vijftien onderzochte velden aanwezig en is hydra:totalItems een integer; er is geen volgende pagina. De vijf niet-lege verwachte collecties hebben een overeenkomend totaal; de UTC-dagcollectie wijkt af van het verwachte totaal nul.

### Contractafwijkingen en gevolgen

- **TZ-001 — bevestigd voor de geteste kwartierqueries:** querytijdzone 1 bepaalt de Nederlandse daggrenzen, terwijl de records tijdzone-ID 0 hebben. De drie geteste dagen hebben volledige dekking met 92, 100 en 96 kwartieren. De validator verwachtte ten onrechte altijd gelijkheid van query- en response-ID. Behandel querytijdzone en recordtijdzone als verschillende concepten; valideer de overige dimensies en de werkelijke tijdstempels onafhankelijk. Generaliseer dit nog niet naar andere granulariteiten of datasets.
- **TZ-002 — open:** de NL-dagaggregatie op 25 oktober bevat één record met ID 1, maar de UTC-intervalgrenzen wijken af van de verwachte Nederlandse kalenderdag. Verwacht: 24 oktober 22:00 UTC tot 25 oktober 23:00 UTC, een interval van 25 uur. De gerichte vervolgprobe bevestigt een ontvangen duur van 24 uur, een beginoffset van 0 s en eindoffset van -3600 s. De kalenderdekking is onvolledig; de betekenis van het volume in dit record is niet bewezen.
- **TZ-003 — open:** de UTC-dagaggregatie retourneert één record met ID 0, hoewel de handleiding een beperking tot tijdzone 1 vermeldt. De gerichte vervolgprobe bevestigt 24 uur duur maar een begin- en eindoffset van +82800 s (+23 uur). De oude verwachting nul records is weerlegd, evenals de hypothese van exacte UTC-kalenderdekking voor deze aanvraag.

**Implementatiebeperking:** gebruik een dagaggregatie uit de API niet als bewezen bron voor energie- of forecastberekeningen zolang TZ-002/TZ-003 openstaan. Voor toekomstige Nederlandse kalenderaggregaties zijn gevalideerde UTC-kwartierintervallen het aangewezen vertrekpunt; controleer dekking en meetsemantiek voordat volumes worden opgeteld. Geen automatische reparatie van upstream-tijdstempels, geen stilzwijgende acceptatie van onjuiste intervallen.

**Vastgelegd implementatiebesluit (24 november 2026):** productieaanvragen gebruiken standaard granularity 4 (kwartier) en granularitytimezone 0 (UTC). Bereken Nederlandse kalendergrenzen met ZoneInfo("Europe/Amsterdam"), converteer beide lokale middernachten afzonderlijk naar UTC, vraag de overlappende UTC-kalenderdagen begrensd op en selecteer het halfopen doelinterval. Valideer volledige kwartierdekking (92/96/100 intervallen), revisies, classificatie en meetsemantiek voordat lokale dagtotalen worden berekend. Zie de canonieke procedure in [integratieplan §15](INTEGRATION_PLAN.md#15-tijdzonebeheer-en-historie). Dit is een gekozen implementatiestrategie; samengestelde kalenderqueries en berekeningen zijn nog niet productiegevalideerd. De afwijkingen TZ-002/TZ-003 blijven open.

### Gerichte dagaggregatieprobe (TZ-002/TZ-003)

Scope daily voert uitsluitend twee vaste aanvragen uit: nationale historische zon, granularity 6, point 0, activity 1, classification 2, page 1 en itemsPerPage 100. De datums zijn bewust vastgezet om exact de eerdere afwijkingen te reproduceren. Geen nieuwe kwartier-, forecast- of pagineringsaanvragen.

| Referentie | Datumfilter | Query-ID | Verwachte UTC-grenzen | Verwachte duur |
| --- | --- | --- | --- | --- |
| TZ-002 | 2026-10-25 tot 2026-10-26 | 1 | 2026-10-24 22:00 tot 2026-10-25 23:00 | 90000 s (25 uur) |
| TZ-003 | 2026-11-22 tot 2026-11-23 | 0 | 2026-11-22 00:00 tot 2026-11-23 00:00 | 86400 s (24 uur; hypothese) |

De eerdere verwachting van een lege UTC-dagcollectie is weerlegd; toets nu één record met exacte UTC-kalenderdekking. Dit is een testhypothese en nog geen contractgarantie. Bij precies één geldig record rapporteert de probe expected_duration_seconds, observed_duration_seconds, start_offset_seconds en end_offset_seconds. Offset is ontvangen grens min verwachte grens; nul betekent gelijk, negatief eerder, positief later. Bij nul of meerdere records zijn de drie ontvangen timingmetingen null en faalt de dekking. De probe rapporteert geen ruwe tijdstempels of energiewaarden. Beide aanvragen worden uitgevoerd bij gewone dekkingsafwijkingen; transport-, schema- en veiligheidsfouten stoppen direct. De eindstatus blijft failure bij een afwijkende dekking, telling of response-ID. Full en timezone blijven beschikbaar voor regressieonderzoek; de bestaande strikte kwartier-ID-vergelijking in die scopes blijft ongewijzigd en kan voor TZ-001 een bekende afwijking melden.

Offline: 17 contracttests geslaagd op Python 3.13.5 (inclusief drie nieuwe tests voor de vaste dagquery's, duur en afzonderlijke grensafwijkingen, correcte UTC-dagdekking en lege collecties). Compileall geslaagd. [Baseline CI-run 45476735384](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45476735384): Ruff-lint, Pylint, strict mypy, offline tests, documentatievalidatie en dependency-audit geslaagd; uitsluitend Ruff-format signaleerde een Query-aanroep. De formattering is exact volgens de CI-diff hersteld, zonder gedragswijziging. [Herhaalde Baseline CI](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45478357087) geslaagd; [PR #16](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/pull/16) gemerged. Dagaggregaties blijven uitgesloten van bewezen productiegedrag totdat de semantiek is vastgesteld.

### Live-resultaat scope daily — 24 november 2026

[Run 45478763623](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45478763623/job/138745945524) op main (`a790d0dea5c98e12582911e3f3a7e1dbb6c94db8`) heeft beide vaste query's uitgevoerd. De ontvangen duur en beide grensoffsets zijn numeriek, wat volgens de probe exact één interval betekent. Beide response-timezone-ID's komen overeen met de query. De run eindigde terecht met exitcode 1.

| Referentie | Verwachte duur (s) | Ontvangen duur (s) | Beginverschil (s) | Eindverschil (s) | Exacte dekking |
| --- | ---: | ---: | ---: | ---: | --- |
| TZ-002 | 90000 | 86400 | 0 | -3600 | Nee |
| TZ-003 | 86400 | 86400 | +82800 | +82800 | Nee |

TZ-002: het interval begint correct maar eindigt een uur te vroeg. Dit bewijst geen ontbrekende energiewaarde of vaste 24-uursimplementatie voor alle dagen. TZ-003: het interval is 23 uur verschoven; duur alleen is geen dekkingsbewijs. De oorzaak van beide afwijkingen en de meetsemantiek blijven onbekend. Geen automatische tijdstempelcorrectie, geen versoepeling van validatie en geen productiegebruik van dagaggregaten. Behoud de eerdere waarnemingen als regressiebewijs; vraag de API-leverancier om verduidelijking van daggrenzen, datumfilters, tijdzone-ID 0 en DST. Een volgende live-probe vereist een afzonderlijke hypothese, begrensde scope en expliciete autorisatie; herhaal niet zonder nieuwe onderzoeksvraag. Geen nieuwe live-aanvragen bij deze documentatiewijziging.

## Meetsemantiek: broncontrole en bestaande loganalyse — 24 november 2026

De officiële [definities](https://ned.nl/nl/definities) bevestigen intervalvolume en de naar uurwaarde omgerekende capaciteit; voor 15 minuten geldt capacity = 4 × volume. De [handleiding](https://ned.nl/nl/handleiding-api) noemt kW, kWh, kg en kg/kWh. De benuttingsformule (capacity gedeeld door percentage geeft maximale effectieve capaciteit) ondersteunt een eenheidsloze ratio, evenals de voorbeeldwaarde en live tellingen; exacte schaal, toepasselijkheid, afronding en bereik blijven te verifiëren. De OpenAPI-omschrijving van emission in ton is tegenstrijdig met de handleiding in kg. Geen automatische kg/ton-conversie zonder bevestiging.

Heranalyse van [live-job 138729707092](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45474134929/job/138729707092): tien nationale P0-responses van 96 records plus twee pagina's van 48 voor de herhaalde historische zonquery (1056 ontvangen records, niet 1056 unieke intervallen). Alle vijf metrieken hebben nul ontbrekende, null of negatieve waarden. Percentage is nooit boven één. In de tien primaire responses:

| Type | Nul capacity/volume/percentage current | Nul capacity/volume/percentage forecast | Nul emission/emissionfactor per classificatie |
| --- | --- | --- | --- |
| 1 | 7 / 7 / 7 | 0 / 0 / 0 | 96 / 96 |
| 2 | 63 / 63 / 63 | 64 / 64 / 64 | 96 / 96 |
| 51 | 0 / 0 / 0 | 0 / 0 / 0 | 96 / 96 |
| 27 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 |
| 59 | 0 / 0 / 96 | 0 / 0 / 96 | 96 / 96 |

Deze marginale tellingen bewijzen geen recordgewijze relatie of algemene nullability. De [datacatalogus](https://ned.nl/nl/datacatalogus) noemt emissies voor 1/2/51 niet toepasselijk, voor 59 niet beschikbaar, voor 27 wel beschikbaar. Presenteer nul op niet-ondersteunde velden niet als bewezen emissiemeting; type 59-percentage niet als bewezen benuttingsmeting. Houd ontbrekend, null, nul, niet-toepasselijk en ongeldig afzonderlijk. De changelog v1.26.0 en v1.27.0–1.27.1 bevestigt herberekeningen en tijdelijke vervanging van current door forecasts; classificatie is geen garantie op bemeten data.

### Gerichte kwartiersemantiekprobe (scope semantics)

Nieuwe opt-in scope met zes afzonderlijke nationale UTC-kwartierqueries, page 1, itemsPerPage 100, gebruikelijke halfopen datumfilters: types 1/2/51/27/59, classification 2, vaste datum 2026-11-22; type 27, classification 1, morgen ten opzichte van uitvoeringsdatum UTC. Geen dagaggregatie, herhaalde paginering of fout-/belastingtest. Hypothesen:

- Capacity en volume: tel exacte gelijkheid van capacity = 4 × volume, afwijkingen tot en met 3 kW, grotere afwijkingen en niet-vergelijkbare ontbrekende/null-waarden. De 3 kW-band is uitsluitend een diagnostische keuze om mogelijke integerafronding te signaleren, geen gedocumenteerde tolerantie of productieregel.
- Alleen type 27: bij positieve volume, factor en emission toets emission versus volume × emissionfactor (kg) en emission × 1000 versus hetzelfde product (tonhypothese); tel overeenstemming binnen 1% relatieve afwijking, geen overeenstemming, niet-positieve en niet-beschikbare waarden. De 1%-band is uitsluitend een diagnostische keuze; geen unitgarantie of acceptatiegrens. Geen afleiding uit nulwaarden of vergelijking voor niet-ondersteunde datasets.
- Bestaande metriek-, veldtype-, dimensie-, paginering- en intervaldekkingcontroles blijven behouden. De nieuwe uitvoer bevat alleen categorieaantallen; geen ruwe waarden, ratio's, residuals of identifiers. Een geslaagde workflow betekent alleen structurele contractobservatie; de semantische tellingen moeten apart worden beoordeeld.

[Eerste Baseline CI van PR #21](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45484642366/job/138766646265): offline maintenance-tests, Ruff-lint, Pylint, strict mypy, documentatievalidatie en dependency-audit geslaagd op de gelockte baseline. Alleen Ruff-format faalde op scripts/test_ned_contract_extended.py:269 (assertEqual-aanroep over drie regels); exact de CI-formatterdiff toegepast, zonder testlogica te veranderen. [Herstelcommit 4a0bca6](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/commit/4a0bca648e68e50587a62f1d951df098cd50d0be); [herhaalde Baseline CI](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45485551617/job/138769838010) geslaagd, inclusief Ruff-format, Ruff-lint, offline maintenance-tests, Pylint, strict mypy, documentatie, synthetische runtime-wheelproef en audit. Regressie vastgelegd in de [kwaliteitsverificatieskill](../.agents/skills/ha-quality-verification/SKILL.md). De probe is na merge van PR #21 live uitgevoerd; zie resultaten hieronder. Leveranciersverduidelijking blijft vereist voor emission-eenheid/afronding, percentage-schaal en niet-toepasselijke waarden, TZ-002/TZ-003, revisies, forecastgrenzen en fout-/ratelimitsemantiek. Geen nieuwe live-aanvragen zonder expliciete autorisatie.

### Live-resultaat scope semantics — 24 november 2026

[Live-job 138771818423](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45486109474/job/138771818423) op main (aef5851c0b681feb8676d544a870a5120d534889), handmatig gestart: success. Alle zes nationale UTC-kwartierqueries leveren 96 records, exacte dekking, correcte dimensies en response-timezone-ID 0, overeenkomende totalItems en geen volgende pagina. Voor alle 576 ontvangen records zijn de vijf metrieken aanwezig, niet-null, niet-negatief en eindig; percentage nergens boven één. Historie: 22 november 2026; type 27 forecast: 25 november 2026. Geen bewijs voor andere dagen, regio's, horizon of algemene nullability.

| Type | Classificatie | Exact capacity = 4 × volume | Afwijking > 0 t/m 3 kW | Afwijking > 3 kW | Niet vergelijkbaar |
| --- | --- | ---: | ---: | ---: | ---: |
| 1 | 2 | 14 | 58 | 24 | 0 |
| 2 | 2 | 63 | 25 | 8 | 0 |
| 51 | 2 | 23 | 73 | 0 | 0 |
| 27 | 2 | 96 | 0 | 0 | 0 |
| 59 | 2 | 22 | 74 | 0 | 0 |
| 27 | 1 | 96 | 0 | 0 | 0 |
| Totaal | | 314 | 230 | 32 | 0 |

SEM-001: de gedocumenteerde exacte relatie is weerlegd als universele recordregel; 32 records (type 1 en 2) vallen buiten de diagnostische 3 kW-band. Ook de 230 kleinere afwijkingen bewijzen geen afrondingsmethode. Gebruik geldig API-volume als primaire energiebron; behoud capacity en volume onafhankelijk, geen automatische overschrijving, afgeleide fallback of afkeur uitsluitend op basis van deze diagnostiek. Vraag leverancier naar eenheden, precisie, model- en aggregatieverschillen. Dit is geen bewijs dat een van beide waarden onjuist is.

| Type 27 | Kg binnen 1% | Ton binnen 1% | Geen overeenkomst | Niet-positief | Niet beschikbaar |
| --- | ---: | ---: | ---: | ---: | ---: |
| Current | 96 | 0 | 0 | 0 | 0 |
| Forecast | 96 | 0 | 0 | 0 | 0 |

SEM-002: alle 192 positieve vergelijkingen ondersteunen emission in kg bij de gedocumenteerde volume-eenheid kWh en emissionfactor kg/kWh; geen enkele ondersteunt ton. Sterk runtimebewijs voor de twee geteste type 27-queries, overeenkomstig de handleiding. De formele OpenAPI-tegenstrijdigheid en afronding blijven open; geen automatische kg/ton-detectie of tolerantie als productiecontract. De 1%-band is diagnostisch. Percentage-schaal, niet-toepasselijkheid, revisies, volledige forecasthorizon en foutsemantiek blijven open. Geen nieuwe live-aanvragen nodig voor registratie.

## Handmatige bereikbaarheidsdiagnostiek — 24/25 november 2026

Bron: vijf door de eigenaar aangeleverde geschoonde JSON-logfragmenten van het zelfstandige lokale script `ned_api_url_test.py`, buiten de repository en buiten GitHub Actions. Uitvoering van 24 november 2026 22:48:31 UTC tot 23:04:27 UTC (24 november 23:48 tot 25 november 00:04 Nederlandse tijd). De beschikbare scriptkopie is geïnspecteerd; SHA-256 aa14e79b63d5cec61747b0e9fbdcbb08afbf44d20ba7041a8134e2622471f019. De exacte hash van het door de eigenaar uitgevoerde exemplaar is niet afzonderlijk bevestigd. Geen onafhankelijke heruitvoering of nieuwe live-aanvragen door de projectagent. Alleen samengevatte metadata, geen API-key, ruwe response, record-ID of accountgegevens.

| Starttijd UTC (24 november) | Scope | Geslaagd / zichtbaar |
| --- | --- | --- |
| 22:48:31 | Zeven openbare URL's | 7/7 |
| 22:59:23 | Eén geauthenticeerde UTC-kwartierquery; opdracht niet meegeleverd | 1/1 |
| 23:01:16 | Extra URL 1; exacte URL niet meegeleverd | 1/1 |
| 23:01:51 | Historische dataset 51, 22 november 2026 | 1/1 |
| 23:04:27 | --urls --api --day 2026-11-22; standaard dataset 2 | 8/8 zichtbare resultaten |

Totaal 18/18 gerapporteerde controles met HTTP 200 en passed=true: 14 openbare standaard-URL-controles, één extra URL en drie geauthenticeerde API-controles. Herhaalde verzoeken zijn geen unieke endpoints of datasets. Van de laatste uitvoering ontbreekt de afsluitende samenvatting/exitstatus in het aangeleverde fragment; de acht individuele resultaten zijn wel aanwezig.

### Openbare documentatie

| URL-label | Bytes, beide metingen | Eerste ms | Tweede ms | Gerapporteerd MIME-type |
| --- | ---: | ---: | ---: | --- |
| NED website (API-overzicht) | 64121 | 3243 | 1210 | text/html |
| API-handleiding | 70607 | 170 | 141 | text/html |
| Datadefinities | 79121 | 173 | 117 | text/html |
| Datacatalogus | 84514 | 155 | 130 | text/html |
| API-changelog | 75506 | 126 | 154 | text/html |
| Swagger | 447 | 1125 | 95 | other/unknown |
| OpenAPI JSON | 100234 | 166 | 117 | other/unknown |

Beide OpenAPI-metingen melden 22 paden en 100234 bytes, overeenkomend met de eerder vastgelegde export. De huidige log bevat geen SHA-256 van de responses; inhoudelijke identiteit is niet bewezen. De beschikbare scriptkopie vraagt de export op via https://api.ned.nl/v1/docs.jsonopenapi?spec_version=3. De code normaliseert Content-Type naar een vaste allowlist; other/unknown omvat zowel ontbrekende als niet-geallowliste MIME-types. Het is geen bewezen serverfout en de oorspronkelijke header is onbekend. Extra URL 1 levert 447 bytes, other/unknown en 111 ms; gelijke lengte met Swagger bewijst geen gelijke URL of inhoud. De timer omvat de HTTPS-aanvraag en het lezen van de response, geen afzonderlijke serverlatency; de korte meetreeks bewijst geen structurele prestaties.

### Geauthenticeerde kwartierdata

| Scope | Bytes | ms | Records | Volgende link gedetecteerd |
| --- | ---: | ---: | ---: | --- |
| Eerste UTC-query, exacte parameters niet meegeleverd | 50931 | 3232 | 96 | Nee |
| Type 51, historie 22 november | 51844 | 218 | 96 | Nee |
| Type 2 volgens scriptdefaults, historie 22 november | 50931 | 172 | 96 | Nee |

Alle drie melden application/ld+json, HTTP 200, de aanwezigheid van vijftien onderzochte velden en geen waargenomen nullwaarden. De beschikbare scriptkopie bouwt voor de opgegeven datum point=0, activity=1 voor type 2 en 51, classification=2, granularity=4, granularitytimezone=0, page=1, itemsPerPage=100, order[validfrom]=asc en datumfilters met de volgende kalenderdag als exclusieve bovengrens. Alleen de twee opdrachten met expliciete datum zijn in het aangeleverde log herleidbaar tot deze scope; de eerste query is niet als dataset 2 geclassificeerd uitsluitend op basis van responsegrootte.

| Velden | Waargenomen runtime-typen |
| --- | --- |
| id, capacity, volume, emission, emissionfactor | int in alle drie |
| percentage | int en float in eerste en laatste query; uitsluitend float in type 51 |
| point, type, activity, classification, granularity, granularitytimezone | str in alle drie |
| validfrom, validto, lastupdate | str in alle drie |

De gerapporteerde vorm bevestigt bereikbaarheid en toegang voor de uitgevoerde verzoeken (aanvullend bewijs BL-004). Het recordaantal is consistent met 96 kwartieren, maar het script valideert geen unieke intervallen, tijdstempelinhoud, UTC-offset, volledige dekking, volgorde, dimensiewaarden, totalItems, revisies, meetwaarden, eenheden of pagineringsgedrag op een tweede pagina. Geen bewijs voor NED-productiecompatibiliteit van NedTransport: dit zelfstandige script gebruikt de standaardbibliotheek. Geen nieuw bewijs voor TZ-001/002/003 of SEM-001/002, geen leveranciersantwoord of nieuwe fasevrijgave. BL-003 blijft open; geen identieke nieuwe live-probe zonder concrete hypothese en expliciete autorisatie.

## Leveranciersverduidelijking

Het [conceptverzoek aan NED](NED_CONTRACT_QUESTIONS.md) bundelt SEM-001, SEM-002, TZ-001/002/003 en de resterende contractvragen. Status: verzending per e-mail op 24 november 2026 door eigenaar bevestigd; in afwachting van leveranciersantwoord. Geen nieuwe live-observatie. De verzonden tekst en aflevering zijn niet onafhankelijk gecontroleerd. De officiële [handleiding](https://ned.nl/nl/handleiding-api) bevestigt bovendien dat lastupdate kan wijzigen door herberekening zonder wijziging van de intervalwaarde; behandel een gewijzigde timestamp niet automatisch als gewijzigde energie-inhoud. Stabiele revisiesleutel, selectievolgorde, verwijdering en herkomst blijven te bevestigen.

## Handmatige authenticatieobservaties — 25 november 2026

Bron: drie door de eigenaar aangeleverde, geschoonde JSONL-uitvoeren van het zelfstandige script ned_api_auth_test.py, buiten CI. Starttijdstempels UTC: 2026-11-24T23:49:23.391223+00:00, 2026-11-24T23:51:04.284524+00:00 en 2026-11-24T23:51:33.869565+00:00 (25 november 00:49–00:51 CET). Geen eigen heruitvoering, geen verificatie van de precieze uitgevoerde scriptversie of sleutelrechten. De eerste twee opdrachtregels bevatten geen --limited terwijl de uitvoer vier scenario's bevat; bij de derde opdrachtregel staat --limited wel expliciet. Alle uitvoerregels melden negative_tests_authorized_by_operator=true; toestemming van NED is niet onafhankelijk vastgesteld.

Vaste scope: GET https://api.ned.nl/v1/utilizations, page=1, itemsPerPage=100, order[validfrom]=asc, point=0, type=2, activity=1, classification=2, granularity=4, granularitytimezone=0, validfrom[after]=2026-11-22, validfrom[strictly_before]=2026-11-23. Alle drie runs rapporteren vier geplande en vier waargenomen requests; twaalf HTTP-responses, geen transportfouten. Het gaat om herhaalde waarnemingen voor één query, niet twaalf onafhankelijke contractscenario's.

| Referentie | Scenario | Status (runs 1/2/3) | Mediatype | Bytes | Responstijd ms (1/2/3) |
| --- | --- | --- | --- | ---: | --- |
| AUTH-001 | Geldige controle | 200/200/200 | application/ld+json | 50931 | 3283/188/128 |
| AUTH-002 | Ontbrekende header | 401/401/401 | application/ld+json | 171 | 85/104/112 |
| AUTH-003 | Ongeldige key | 403/403/403 | application/json | 80 | 110/109/129 |
| AUTH-004 | Verondersteld beperkte key | 200/200/200 | application/ld+json | 50931 | 167/162/102 |

AUTH-001 en AUTH-004: collecties bevatten elk 96 records met overeenkomende dimensies. AUTH-002: JSON-object met hydra:title en hydra:description; AUTH-003: JSON-object met message. Geen ruwe foutteksten, sleutelgegevens of accountgegevens beschikbaar of opgeslagen. AUTH-005: bij alle twaalf responses ontbreken WWW-Authenticate, Retry-After en Location; dit bewijst niets over headers bij andere statussen. Alle drie samenvattingen melden completed=false, contract_confirmed=false, limited_key_tested=true, stop_reason=unexpected_data_access. AUTH-004 bevestigt toegang tot de geteste query, niet het bestaan of ontbreken van rechtenbeperkingen. De gelijke responsomvang bewijst geen identieke inhoud. De operatorgerapporteerde 12 observaties bevestigen geen algemene statusgarantie of formeel leverancierscontract.

**Implementatiebesluit (eigenaarsopdracht 25 november 2026):** in PR #39 krijgt de conceptauthenticatieclient voor HTTP 401 de specifieke NedAuthenticationError en voor 403 de onafhankelijke NedAccessDeniedError (geen subklasse van NedAuthenticationError of NedPermissionError). Classificeer de geobserveerde HTTP-status vóór validatie van het success-mediatype; parse of log geen fouttekst. Een 403 kan ook ongeldige credentials betekenen; geen automatische reauth bij 403. De Config Flow toont invalid_auth respectievelijk access_denied; de laatstgenoemde vraagt om controle van zowel sleutel als rechten. Onbekende statussen, lege collecties en ongeldige responses blijven inconclusief; 429/5xx-contractmapping en Retry-After blijven open. De eerdere gesloten Config Flow-koppeling wordt voor de beperkte lokale alpha vervangen door de echte positieve controle uit §21.2 van het integratieplan; geen volledige fasevrijgave. Synthetische tests zijn geen live bewijs. Herhaal deze identieke negatieve probes niet; verder autorisatieonderzoek vereist een aantoonbaar beperkte key of leveranciersinformatie, een nieuwe hypothese en expliciete toestemming. Geen opzettelijke rate-limitproeven.

## Beperkte lokale alpha — 25 november 2026

Op eigenaarsopdracht van 25 november 2026 (herstel van de concrete technische blokkades voor een afzonderlijke Home Assistant-alpha) wordt alleen het aantoonbaar onderzochte deel voor een lokale proef uitgewerkt: positieve historische sleutelvalidatie en vijf nationale current-capacity-datasets (type 1, 2, 51, 27 met activiteit 1; type 59 met activiteit 2; point 0, granularity 4, timezone 0, classification 2). AUTH-001/002/003 en de eerdere kwartierproeven zijn de grondslag; geen algemene contractgarantie. Geen live uitvoering door AI, geen negatieve probes, geen publicatie. Vrijgave voor een eigenaarstest pas na geslaagde volledige CI en lokale wheelverificatie in een afzonderlijke Core-testomgeving. CO₂, forecast, hernieuwbaar aandeel, dagaggregaten, revisieselectie en onbewezen autorisatie-/rate-limitsemantiek blijven buiten actieve scope. Volledige faseacceptatie, kwaliteitsdrempels en releasepoorten blijven ongewijzigd.

De alpha gebruikt capacity rechtstreeks in kW (suggestie MW), geen omzetting vanuit volume en geen reparatie van SEM-001. Query één UTC-dag met page=1 en itemsPerPage=100, maximaal 96 records; valideer mediatype, hydra:member, integer totalItems, afwezigheid van next-links, alle zes IRI-dimensies, eindige niet-negatieve numerieke capacity en unieke exact uitgelijnde UTC-kwartieren binnen het dagvenster. Ontbrekende intervallen blijven ontbrekend, echte nul blijft nul; dubbele revisies en onverwachte paginering falen gesloten. Alleen kwartieren die bij requestaanvang én ontvangst gesloten zijn, komen in aanmerking; receipt timestamp wordt vastgelegd en de voorlopige intervalgrens blijft 30 minuten. Per refresh maximaal vijf logische dagqueries, nabij UTC-middernacht maximaal tien; geen applicatieretries. Core maakt sessies met behoud van de native SSRF-middleware en extra per-attempt-middleware; flow-sessie detach in finally, entry-sessie native unload. Eén proceslokaal budget van 120 pogingen per 300 seconden telt ook aiohttp-interne GET-retries en fouten. Gewone zelfstandige geleende sessies zonder eigen retry-middleware reserveren conservatief twee slots per logische call op de gelockte aiohttp-baseline. Niet-200 status vóór bodyvalidatie; 429 blokkeert direct bij headers, geldige HTTP Retry-After seconden of datum worden genormaliseerd; minimum 300 seconden, langere geldige instructies respecteren, boven 24 uur procesblok. Dit is defensief HTTP-beleid, geen bewezen NED-quota- of headercontract. HTTP 401 leidt tot auth-fout; 403 en andere datasetfouten blijven per dataset geïsoleerd met geschoonde logcontext, geen automatische reauth bij 403. Alle datasets mislukt of globale 401/429 faalt de batch. Automatisch herstel bij volgende succesvolle refresh. Geen oude waarden voor mislukte datasets. Alleen currentcoordinator actief. Zie [PR39_REVIEW.md](PR39_REVIEW.md).

## Openstaande verificatie

- [x] OpenAPI-export ophalen, parsen en relevante schema's, filters, responses en security scheme inspecteren; verschillen vastgelegd.
- [x] Eerste geautoriseerde begrensde read-only contractobservatie: nationale zon, current/historie en forecast, status, content-type en veldtypen.
- [x] Nationale P0-combinaties voor beide classificaties, UTC-kwartierdata en IRI-dimensies voor de geteste dagen.
- [x] Paginering 48 + 48 en veilige next-link voor de geteste nationale zonquery.
- [x] Voor nationale historische zonne-energie: Nederlandse kwartierdekking op 23-, 24- en 25-uursdagen, response-ID 0 bij query-ID 1 (TZ-001).
- [x] Gerichte dagprobe uitgevoerd: TZ-002/TZ-003 reproduceerbaar aangetoond voor de twee vaste queries; geen bewijs van correct contractgedrag.
- [ ] Verklaar TZ-002/TZ-003 met leveranciersinformatie; verifieer lege resultaten, overige datumfilters en dagaggregatiesemantiek.
- [x] Gerichte scope semantics uitgevoerd en beoordeeld: 576 records, 32 afwijkingen buiten 3 kW, 192 kg-hypotheseovereenkomsten.
- [ ] Verklaar SEM-001 en bevestig SEM-002 formeel, afronding, null versus nul, percentage-schaal, volledige forecastdekking en revisies.
- [x] Handmatig gerapporteerde authenticatieobservaties AUTH-001/002/003/005 voor één vaste query vastgelegd; drie herhalingen, geen eigen live uitvoering.
- [ ] AUTH-004: bevestig autorisatie-/rechtensemantiek, algemene authenticatiestatusmapping, rate-limit-scope en Retry-After met leveranciersinformatie of normaal waargenomen gedrag. Geen herhaling van identieke negatieve tests of opzettelijke limietoverschrijding.
- [ ] Leg geschoonde fixtures en concrete verificatieresultaten vast; onderscheid synthetische tests van live bewijs.

## Veilige toegang (BL-004)

De [opt-in workflow](../.github/workflows/api-contract.yaml) en [probe](../scripts/ned_contract_probe.py) zijn voorbereid. De workflow draait uitsluitend handmatig op main met expliciete bevestiging, beperkte leesrechten, een vaste environment ned-contract en een jobtimeout van zeven minuten. De secret wordt alleen in de probestap geïnjecteerd. De eigenaar heeft bevestigd dat de beveiligde environment en sleutel zijn ingesteld. Behoud de deploymentbranchbeperking tot main en vereiste reviewers waar beschikbaar. De environmentinstellingen zijn niet onafhankelijk uitleesbaar via de huidige connector; de succesvolle handmatige uitvoering op main bevestigt werkende secret-injectie. Gebruik uitsluitend een environment-secret NED_API_KEY, geen repositorybrede secret. Plaats nooit een key in chat, issues, code of artifacts.

Scope daily (twee requests, eerdere standaard) is op main uitgevoerd; zie het live-resultaat hierboven. De nieuwe standaard semantics vraagt zes kwartierqueries en vereist opnieuw expliciete bevestiging. Start een nieuwe NED API contract observation uitsluitend bij expliciete autorisatie en een concrete onderzoeksvraag, met passende vaste scope en confirm_live. De [uitgebreide probe](../scripts/ned_contract_extended.py) voert maximaal 18 sequentiële GET-verzoeken uit, zonder retries, redirects of willekeurige URL's. De oorspronkelijke twee-waarnemingenprobe blijft beschikbaar voor offline regressietests. Sockettimeout 15 s, per response maximaal 2 MiB, uitsluitend de vaste TLS-host, geen account-/gebruikersendpoints. Stop bij de eerste transport-, veiligheids- of schemafout; bekende tijdzoneafwijkingen en afwijkende geldige totaaltellingen bij één pagina worden verzameld en resulteren in failure. De uitvoer bevat uitsluitend vooraf bekende querydimensies, dagen, bekende response-timezone-ID's, tellingen, veldtypen en booleans; geen ruwe energiewaarden, headers, identifiers, next-links of payloads.

### Uitgebreide contractmatrix (BL-003)

| Scenario | Requests | Verwachte contractcontrole |
| --- | ---: | --- |
| Nationale P0 types 1, 2, 51, 27, 59 | 10 | Per type current twee dagen geleden en forecast morgen; 96 UTC-kwartieren, activity 2 alleen voor type 59 |
| Paginering nationale zon | 2 | 48 + 48 records, exact volgende query, totaal 96, geen extra pagina |
| NL-tijdzone kwartierdata | 3 | 29 maart 2026: 92, 25 oktober 2026: 100, twee dagen geleden: kalenderdaglengte berekend via Europe/Amsterdam |
| NL-dagaggregatie | 2 | Eén interval van 23 respectievelijk 25 uur op de vaste DST-datums |
| UTC-dagaggregatie | 1 | Eén record met exacte UTC-dagdekking (24 uur; hypothese weerlegd voor de geteste query, TZ-003) |

Controleer gedocumenteerde IRI's voor alle zes dimensies, id-type, UTC-aware validfrom/validto/lastupdate, strikt positieve intervalduur, oplopende en volledige intervaldekking, hydra:member, totalItems en paginalimieten. Next-link moet dezelfde HTTPS-host of een relatief pad en exact de zelf opgebouwde tweede query bevatten; volg de aangeleverde URL nooit rechtstreeks. Elke numerieke metriek moet bij aanwezigheid en niet-null eindig numeriek zijn; booleans en NaN/Infinity worden verworpen. Rapporteer per metriek ontbrekend, null, nul, negatief en groter dan één, zonder conclusies over eenheid of percentage-schaal. De matrix test strikte gedocumenteerde verwachtingen; een contractafwijking kan de run stoppen en moet worden onderzocht, niet stilzwijgend geaccepteerd.

De zes nieuwe offline unittest-methoden gebruiken uitsluitend synthetische gegevens en dekken alle 18 requests, verkeerde dimensies, onveilige next-links, ongeldige getallen/tijdstempels, ontbrekende dekking en redactie. De twaalf contracttests (zes bestaande plus zes nieuwe) zijn lokaal geslaagd op Python 3.13.5. [Eerste Baseline CI-run 45473451958](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45473451958) bevestigt geslaagde offline tests en strict mypy op de exacte Python-versie; Ruff-format en Pylint vonden formatterings- en duplicatiebevindingen, die gericht zijn hersteld. Herhaalde CI op de gemergede commit slaagt; uitgebreide live-run is gedeeltelijk geslaagd zoals hierboven vastgelegd. Twee aanvullende offline regressietests (in totaal veertien contracttests) slagen lokaal op Python 3.13.5; CI van de vervolgprobe is geslaagd in [Baseline CI 45475337532](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45475337532); PR #14 is gemerged. De zes vervolgobservaties zijn uitgevoerd, maar de live-run faalt zoals hierboven beschreven. Een groene run bewijst deze nationale combinaties en tijdvakken, niet alle regio's, horizon, eenheden, foutsemantiek of rate-limit-scope.

De maintenance-probe gebruikt uitsluitend de standaardbibliotheek en is geen productieclient. De zes lokale unittest-tests met gesimuleerd transport zijn geslaagd op Python 3.13.5; eerste Baseline CI-run 45467538518 bevestigt de offline tests en audit. Formatterings- en mock-importbevindingen zijn hersteld; herhaalde CI is geslaagd in [Baseline CI-run 45468321699](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45468321699). De bestaande offline pre-commit-suite voert ze uit. De eerste geauthenticeerde observatie is geslaagd; BL-004 is functioneel afgerond. Volgende live-uitbreidingen vereisen opnieuw expliciete opt-in en een beoordeelde begrensde requestset.

De API-client blijft geblokkeerd totdat het noodzakelijke contract en distributiestrategie zijn gevalideerd. Zie [backlog](BACKLOG.md) en [integratieplan](INTEGRATION_PLAN.md).
