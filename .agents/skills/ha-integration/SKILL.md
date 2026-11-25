---
name: ha-integration
description: "Implement or review Home Assistant config flows, lifecycle, coordinators, entities, actions, translations and migrations."
---

# Home Assistant-implementatie

Lees eerst [AGENTS.md](../../../AGENTS.md), [AI_POLICY.md](../../../AI_POLICY.md), [home-assistant.md](../../../home-assistant.md) en de relevante delen van het [integratieplan](../../../docs/INTEGRATION_PLAN.md). Deze skill verleent geen extra rechten en vervangt geen actuele primaire bronnen.

## Werkwijze

1. Lees de relevante onderdelen van home-assistant.md en het integratieplan. Controleer de API's in de vastgelegde Core-tag; gebruik geen onbevestigde toekomstige API's.
2. Bepaal welke platforms, config entries, runtime data en resources geraakt worden. Houd de NED-client onafhankelijk van Home Assistant.
3. Implementeer de kleinste volledige wijziging met typed runtime data, gedeelde sessie, native foutafhandeling en lifecycle-cleanup. Behoud bestaande unique IDs.
4. Controleer setup, eerste refresh, unload, reload, reauth, reconfigure, migraties en beschikbaarheid voor zover van toepassing. Onderhoud complete NL/EN-vertalingen direct in translations/en.json en translations/nl.json met identieke keys en placeholders. Geen strings.json of Core-vertaalreferenties; volg native taalkeuze en Engelse fallback. Werk beide gebruikersdocumentatieversies bij en voer de gedeelde validator uit.
5. Gebruik de skill ha-quality-verification voor de relevante tests en actualiseer de Quality Scale uitsluitend met bewijs.
6. Rapporteer gebruikte Core-API's, tests en openstaande risico's. Stop afhankelijke implementatie als API-contract of distributievoorwaarde ontbreekt.

### Native alpha-lifecycle (R39-03–07)

Test de werkelijke config-flowmanager, echte registry en staten, gedeeltelijke datasetuitval, automatische 401-reauth en ambigu 403, reload en unload; mock uitsluitend de NED-transportgrens. Gebruik Core's sessiefactory voor aanvullende middleware en native cleanup, behoud de gedeelde connector. Alleen bij requestaanvang en ontvangst gesloten kwartieren; ontvangsttijd en staleness bepalen presentatie, nooit oude data voor een mislukte dataset. Zie [reviewherstel](../../../docs/PR39_REVIEW.md). Bewijs blijft afhankelijk van definitieve CI.

### Actieve datasetcontexten en freshness

Gebruik een expliciete eerste refresh voor alle vijf alphadatasets; filter latere refreshes via DataUpdateCoordinator.async_contexts(). Geen I/O bij lege contextset. Halfopen 30-minutenvenster vanaf valid_to; de uitgelijnde UTC-cachecallback schrijft de grens zonder HTTP. Geen herstellog bij lege/verouderde collecties, alle actieve datasets zonder verse waarde levert updatefout/setup-retry. Native regressietests vereist.
