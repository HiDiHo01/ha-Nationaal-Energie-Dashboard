---
name: energy-data-semantics
description: "Validate energy, power, CO2, forecast, interval aggregation, statistics and DST semantics for NED datasets."
---

# Energiedata en tijdreeksen

Lees eerst [AGENTS.md](../../../AGENTS.md), [AI_POLICY.md](../../../AI_POLICY.md), [home-assistant.md](../../../home-assistant.md) en de relevante delen van het [integratieplan](../../../docs/INTEGRATION_PLAN.md). Deze skill verleent geen extra rechten en vervangt geen actuele primaire bronnen.

## Werkwijze

1. Controleer bronunit, meetinterval, classificatie, activiteit en betekenis in de NED-datacatalogus. Neem geen aan dat utilization vermogen of percentage betekent zonder bewijs.
2. Gebruik timezone-aware datetimes en UTC intern; gebruik Europe/Amsterdam voor kalenderaggregaties. Test overgangen naar zomer- en wintertijd, ontbrekende intervallen en revisies.
3. Gebruik gemeten volume waar beschikbaar. Bereken energie uit vermogen alleen wanneer de bronsemantiek dat rechtvaardigt. Controleer dimensies bij omzettingen en weeg CO2-intensiteit naar energie.
4. Scheid forecasts van actuele statistieken; gebruik geen TOTAL_INCREASING voor intervalenergie. Nationale data is geen huishoudelijke productie of verbruik.
5. Test grenswaarden, negatieve waarden waar geldig, null, nul, NaN, onvolledige dekking, gelijke scores en vroegste optimale vensters. Verifieer HA device/state classes tegen de actuele sensordocumentatie.
6. Documenteer semantische keuzes, dekking, onzekerheid en tests; gebruik ha-quality-verification.

## Dagaggregatie: grenzen afzonderlijk valideren

Controleer bij iedere kalenderaggregatie de verwachte start, het exclusieve einde en de duur onafhankelijk. Een juiste response-tijdzone-ID, recordtelling of duur bewijst geen juiste kalenderdekking. Bereken de verwachte kalendergrenzen in de gevraagde tijdzone en vergelijk in UTC; offsets zijn ontvangen minus verwacht. Gebruik 92/96/100 kwartieren voor de Nederlandse 23/24/25-uursdagen waar volledige kwartierdekking is bevestigd. Tel volumes pas op nadat ook de meetsemantiek is vastgesteld.

Bewezen NED-regressie (24 november 2026, nationale historische zon, granularity 6): [live-run 45478763623](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45478763623/job/138745945524) bevestigt TZ-002 (24 in plaats van 25 uur, begin 0 s, einde -3600 s) en TZ-003 (24 uur, beide grenzen +82800 s). Beide tijdzone-ID's kloppen, beide dekkingen falen. Zie [API_REFERENCE.md](../../../docs/API_REFERENCE.md). Generaliseer niet naar andere datasets of dagen; verander upstream-tijdstempels niet en gebruik deze dagaggregaten niet voor energieberekeningen. Behoud strikte validatie en documenteer oorzaken als onbekend. Nieuwe live-probes uitsluitend bij expliciete autorisatie en een concrete nieuwe hypothese.
