# NED API — contractonderzoek

Peildatum: 24 november 2026. Status: openbare documentatie gecontroleerd; OpenAPI-schema en live contract niet gevalideerd (BL-003).

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

## Openstaande verificatie

De Swagger-pagina is bereikbaar, maar beide machineleesbare exports konden niet worden gelezen: webtoegang accepteert de OpenAPI-mediatypen niet; lokaal curl faalde op DNS. Geen schema, live response of paginering verzinnen.

- [ ] OpenAPI-export uitlezen: schema, vereiste/optionele velden, types, nullability, filters, responses en security scheme.
- [ ] Geautoriseerde begrensde read-only contracttest: één bekend P0-verzoek, current en forecast, status en content-type, vervolgens resterende P0-combinaties.
- [ ] Bevestig paginering, veilige next-links, lege resultaten en datumbereik/offsets; test dagaggregatie en DST.
- [ ] Bevestig meetsemantiek, null versus nul, percentage-schaal, forecastdekking en revisies.
- [ ] Bevestig authenticatie-/autorisatiefouten, rate-limit-scope en Retry-After indien gedocumenteerd of normaal waargenomen. Geen opzettelijke limietoverschrijding.
- [ ] Leg geschoonde fixtures en concrete verificatieresultaten vast; onderscheid synthetische tests van live bewijs.

## Veilige toegang (BL-004)

Voorgestelde secretnaam: NED_API_KEY. Maak eerst een afgeschermde, handmatig gestarte contractworkflow met read-only repositoryrechten, beperkte requests, timeouts en zonder logging van headers of ongeschoonde bodies. Gebruik een aparte testkey in GitHub Secrets (bij voorkeur een beveiligde environment), pas nadat de workflow en toegang zijn beoordeeld. Geen API-sleutel in chat, repository of issue. Er is nog geen contractworkflow of geauthenticeerde aanvraag uitgevoerd. Geen externe gegevensopvraging buiten het expliciete mandaat.

De API-client blijft geblokkeerd totdat het noodzakelijke contract en distributiestrategie zijn gevalideerd. Zie [backlog](BACKLOG.md) en [integratieplan](INTEGRATION_PLAN.md).
