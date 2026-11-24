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
