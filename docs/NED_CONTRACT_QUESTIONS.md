# NED API — verzoek om contractverduidelijking

Datum: 24 november 2026. Backlog: BL-003. Status: concept, niet verzonden; geen leveranciersantwoord ontvangen. Contactkanaal: [NED contact](https://ned.nl/nl/contact). De eigenaar kan het onderstaande verzoek versturen. Geen API-key, accountgegevens, ruwe payloads of recordidentifiers delen. De [contractreferentie](API_REFERENCE.md) bevat de onderzoeksdetails en blijft de canonieke bron.

## Conceptbericht

**Onderwerp: Verduidelijking NED API v1 — kwartierwaarden, CO₂ en tijdzoneaggregaties**

Beste NED-team,

Voor een onafhankelijke Home Assistant-integratie onderzoeken wij het contract van GET /v1/utilizations. Op 24 november 2026 hebben we begrensde read-only controles uitgevoerd. Graag ontvangen we technische verduidelijking van de volgende punten.

1. **SEM-001 — capacity en volume.** De definities beschrijven een relatie van viermaal het intervalvolume bij kwartierdata. Bij point=0, classification=2, granularity=4, granularitytimezone=0, activity=1 en datumfilter 2026-11-22 tot 2026-11-23 wijken 24 van 96 wind-op-landrecords (type 1) en 8 van 96 zonnerecords (type 2) meer dan 3 kW af van capacity = 4 × volume. Is deze relatie exact bedoeld vóór afronding, of worden de velden onafhankelijk berekend? Welke eenheden, precisie, afronding en eventuele modelverschillen gelden? Welk veld is leidend voor intervalenergie?
2. **SEM-002 — CO₂.** De handleiding vermeldt emission in kg, terwijl de OpenAPI-beschrijving ton vermeldt. Voor type 27, activity=1, point=0, granularity=4, timezone=0, current op 22 november en forecast op 25 november 2026 ondersteunen alle 192 positieve vergelijkingen de kg-hypothese binnen 1% van volume × emissionfactor, geen de ton-hypothese. Kunnen jullie bevestigen dat emission in kg en emissionfactor in kg/kWh staan, welke afronding geldt, en of het om productie-intensiteit gaat? Wordt de OpenAPI-beschrijving gecorrigeerd?
3. **TZ-002/TZ-003 — daggrenzen.** Voor historische nationale zon (type=2, point=0, activity=1, classification=2, granularity=6) levert de NL-query (timezone=1, 2026-10-25 tot 2026-10-26) één interval van 86400 seconden in plaats van 90000, met correct begin en einde 3600 seconden te vroeg. De UTC-query (timezone=0, 2026-11-22 tot 2026-11-23) levert ondanks de gedocumenteerde beperking één interval van 86400 seconden, waarvan beide grenzen 82800 seconden te laat liggen. Beide datumfilters gebruiken validfrom[after] en validfrom[strictly_before]. Is dit verwacht gedrag? Hoe worden daggrenzen, DST, volume en de query-/recordtijdzone bepaald? Bij drie NL-kwartierqueries kregen we correcte kalenderdekking, maar response-ID 0 bij query-ID 1 (TZ-001); is dit contractueel bedoeld?
4. **Datakwaliteit en percentage.** Is percentage voor elk P0-type een ratio tussen 0 en 1, een percentage tussen 0 en 100, of kan het buiten dit bereik vallen? Wat betekenen ontbrekende velden, null en nul per metriek? Kunnen niet-toepasselijke velden (zoals emissies voor wind/zon en percentage voor type 59) betrouwbaar worden onderscheiden van echte nulmetingen?
5. **Datumfilters, forecast en revisies.** Wat zijn de exacte inclusieve/exclusieve grenzen en toegestane notaties van de vier validfrom-filters? Welke lege resultaten, forecastdekking, horizon en updatevertraging mogen clients verwachten? De handleiding vermeldt dat lastupdate kan wijzigen zonder gewijzigde intervalwaarde. Welke stabiele sleutel, revisievolgorde en eventuele herkomstindicator voor actuele versus voorspelde data zijn gegarandeerd? Kan een interval achteraf verdwijnen of worden vervangen?
6. **Transport.** Hoe onderscheiden clients ongeldige sleutel, ontbrekende autorisatie en lege collecties? Welke HTTP-statuscodes gelden voor ongeldige filters en throttling? Geldt de limiet van 200 aanvragen per vijf minuten per sleutel, account, IP of andere scope? Wordt Retry-After teruggegeven, en in welk formaat? Is de volgorde en paginering stabiel tijdens revisies?

De genoemde grenzen van 3 kW en 1% zijn uitsluitend diagnostische categorieën, geen door ons veronderstelde API-toleranties. We willen de oorspronkelijke metrieken behouden en Nederlandse kalenderdagen lokaal berekenen uit volledige UTC-kwartierdata, zonder onjuiste upstream-intervallen te corrigeren. Een verwijzing naar de canonieke contractdocumentatie of een schriftelijke bevestiging per vraag zou ons helpen.

Alvast bedankt voor jullie technische toelichting.

Met vriendelijke groet,

## Interne opvolging

- Bronnen: [handleiding](https://ned.nl/nl/handleiding-api), [definities](https://ned.nl/nl/definities), [OpenAPI](https://api.ned.nl/v1), [semantiekprobe](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45486109474/job/138771818423), [dagprobe](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45478763623/job/138745945524).
- De antwoorden zijn nog niet ontvangen. Sluit geen afwijking en verwijder geen acceptatievoorwaarde op basis van dit concept.
- Registreer na ontvangst per vraag bron, datum, toepasselijke dataset, bevestigde garantie en resterende onzekerheid in API_REFERENCE.md; actualiseer plan, backlog en skills en maak waar nodig geschoonde synthetische regressietests.
- Geen identieke nieuwe live-probe. Alleen een concrete nieuwe hypothese met afzonderlijke autorisatie, veilige credentials en begrensd requestbudget.
