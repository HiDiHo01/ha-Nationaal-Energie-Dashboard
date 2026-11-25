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

### Handmatige diagnostiek buiten CI

Leg door de eigenaar aangeleverde logfragmenten vast als handmatig gerapporteerde observaties, niet als eigen heruitvoering. Bewaar UTC-tijd, werkelijk bekende queryscope, aantallen, HTTP-status en geschoonde vormmetadata. Tel herhalingen niet als unieke datasets. Maak onderscheid tussen individuele passed-flags en bewezen exitstatus, MIME-allowlist en oorspronkelijke header, gelijke bestandsgrootte en inhoudshash, recordaantal en gevalideerde intervaldekking. Zie de [18 controles van 24/25 november](../../../docs/API_REFERENCE.md#handmatige-bereikbaarheidsdiagnostiek--2425-november-2026). Geen nieuwe contractgaranties of fasevrijgave op basis van bereikbaarheidsdiagnostiek.

## Beperkte fase-1-vrijgave

Volg de expliciete eigenaarsbeslissing in [integratieplan §21.2](../../../docs/INTEGRATION_PLAN.md#212-fase-1--api-client). Contractonafhankelijke packageconfiguratie, exceptions en generiek transport mogen worden ontwikkeld met synthetische tests. Geen NED-specifieke statusmapping, rate-limitregels, datasetsemantiek, parser of live aanvragen zonder de toepasselijke bevestiging en autorisatie. BL-003 blijft open; volledige faseacceptatie blijft geblokkeerd. Maak geen aannames om de scope kunstmatig te verruimen.

### Generieke transportlaag

NedTransport leent een vertrouwde certificaatvaliderende aiohttp-sessie en voert GET uit tegen één gevalideerde HTTPS-origin. Standaard ClientTimeout(total=15.0) en maximaal 2 MiB verzamelde responsebytes; dit zijn configureerbare interne ontwerpwaarden, geen NED-limieten. Absolute paden zonder URL-componenten, geen redirects, ssl=True, geen automatische decompressie; vraag identity-encoding aan en wijs andere Content-Encoding af. Geef status en bytes terug als immutable TransportResponse (body niet in repr), zonder statusmapping, JSON-parsing, credentials of applicatieretries. Cancellation blijft intact; transportfouten krijgen geschoonde exceptions zonder ruwe exceptionketen. De caller blijft eigenaar van de sessie en levert uitsluitend niet-gevoelige queryparameters. De wire- en TLS-werking, compressiecompatibiliteit en API-contract zijn niet live getest.

Test met synthetische async responsecontexten en streamingchunks; controleer vaste HTTPS-origin, requestopties, exacte bytegrens, encoding, statusbehoud, geschoonde errors en cancellation. Claim geen TLS- of live contractbewijs uit mocks. Valideer de echte wheel en dependencyversies in CI; houd BL-003 open.

### Loopback-HTTPS als aanvulling op mocks

Gebruik [test_transport_https.py](../../../tests/api/test_transport_https.py) voor daadwerkelijke lokale socket- en TLS-regressies. Bind alleen aan IPv4-loopback met een dynamische poort; genereer tijdelijk certificaatmateriaal tijdens uitvoering, vertrouw het uitsluitend in de testcontext en test de afwijzing zonder die trust anchor. Gebruik events voor een gecontroleerd geblokkeerd responsepad; begrens testduur en ruim server, sessie en tasks op. Geen externe requests, geen TLS-validatie uitschakelen, geen vastgelegde sleutels of productiecredentials. Maak onderscheid tussen lokale wirevalidatie, mocks en NED-contractbewijs. [PR #33-baseline](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45499428326/job/138818444788) slaagt op Python 3.14.10: 47 API-tests, 70 statements en 18 branches volledig gedekt, Ruff/Pylint/strict mypy en geïsoleerde wheelinstallatie met gelockte aiohttp/yarl-versies geslaagd. PR #33 gemerged op main 2886a03c033c2ae66a5af368ec5947811e7ce216. Het verschil met 71 lokale statements komt uit de verschillende meetomgevingen; geen gemiste statements in beide rapporten.

### Handmatige authenticatieobservaties (AUTH-001–005)

Zie [API_REFERENCE.md](../../../docs/API_REFERENCE.md#handmatige-authenticatieobservaties--25-november-2026). Drie door de eigenaar gerapporteerde runs reproduceren voor dezelfde query 200 met geldige key, 401 zonder header (JSON-LD) en 403 bij ongeldige key (JSON). De vermeend beperkte sleutel heeft toegang. Map 401 conservatief naar NedAuthenticationError en 403 naar onafhankelijke NedAccessDeniedError; maak geen onderscheid tussen ongeldige key en rechtengebrek op basis van 403 en start daarvoor geen automatische reauth. Classificeer status vóór success-mediatype; geen parsing/logging van ruwe fouttekst. Onbekende statussen, lege collectie en ontbrekende Retry-After blijven onbevestigd. Geen identieke negatieve live probes herhalen. Conceptmapping onder de eigenaarsopdracht is geen volledige contract- of faseacceptatie. Voor de beperkte lokale alpha volgt de Config Flow de afzonderlijke vrijgave in het integratieplan; geen publieke distributie.

### Afgebakende lokale alpha

Volg [integratieplan §21.2](../../../docs/INTEGRATION_PLAN.md#212-fase-1--api-client) en de [contractreferentie](../../../docs/API_REFERENCE.md#beperkte-lokale-alpha--25-november-2026). Alleen de vijf huidige nationale capacity-datasets en positieve historische zonnevalidatie zijn voor een lokale eigenaarstest uitgewerkt; gebruik dezelfde strikte parser voor beide, reject dubbelzinnige revisies en next-links, vul ontbrekende waarden niet aan. Gedeeld proceslokaal budget 120 daadwerkelijke middlewarepogingen per 300 seconden, minstens 300 seconden cooldown bij 429 en respect voor langere geldige HTTP Retry-After; geen claim over upstream Retry-After of quota-scope. Geen nieuwe live probes. [Python-next 45518712696](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45518712696/job/138884782557) op 8207307: 127 zelfstandige API-tests geslaagd. Baseline, volledige integratie en wheelinstallatie moeten opnieuw worden bevestigd. Gebruik uitsluitend de lokale manifest-gepinde wheel volgens [alpha-testinstructies](../../../docs/user/nl/alpha-test.md), geen publieke package-index. Geen publicatie, volledige faseacceptatie of Platinum-claim.

### Status-first en daadwerkelijke pogingen (R39-01/02)

Zie [reviewherstel](../../../docs/PR39_REVIEW.md). Niet-200 status vóór bodyvalidatie, sluit foutresponse zonder payload te lezen. Normaliseer standaard Retry-After zonder ruwe header; extreme geldige delay leidt tot procesblok, geen NED-contractclaim. Core 2026.11.3 biedt async_create_clientsession met toegevoegde middleware; aiohttp 3.14.5 kan intern GET herhalen. Per-attempt reserveert vóór netwerk-I/O, geen private flags, geen verlies van Core SSRF-beveiliging. Gewone geleende sessies zonder extra retry-middleware reserveren twee slots. Test met echte loopback-TLS, concurrency, cancellation, corrupte foutbody en langere cooldown. Geen live tests.

### HTTP asctime-date

RFC 9110 §5.6.7 verplicht herkenning van de obsolete asctime-date als UTC; accepteer uitsluitend de exacte grammatica bij een naïeve datum, geen willekeurige tijdzoneloze datum. Synthetische regressietests voor enkele en dubbele dagcijfers; geen NED-contractclaim.
