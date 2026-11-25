# PR #39 — herstel van de technische review

Scope: lokale alpha 0.1.0a1, vijf nationale power-datasets. Geen nieuwe live NED-verzoeken, geen negatieve probes, geen publicatie, geen volledige faseacceptatie. Bron: [review 6049773362](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/pull/39#pullrequestreview-6049773362). Alle wijzigingen en acceptatie blijven onder AGENTS.md en AI_POLICY.md. De vorige [Baseline CI](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45519191702/job/138886416144) op 9370873 had 168/168 tests, 471 statements/98 branches volledig gedekt; dit is geen bewijs voor de gewijzigde code.

| Review-ID | Herstel | Acceptatie |
| --- | --- | --- |
| R39-01 | Status vóór errorbody, 429 bij headers, Retry-After seconden/datum, langere geldige delay en procesblok boven 24 uur. | Nieuwe offline tests en definitieve CI vereist. |
| R39-02 | Core-sessiefactory behoudt SSRF en telt per-attempt middleware; gewone externe sessies zonder extra retry-middleware reserveren twee slots. | Loopback TLS retry, concurrentie en cancellation; definitieve CI vereist. |
| R39-03 | Native config flow, registries, states, partial recovery, reauth, reconfigure, reload, unload, geen late requests en setup retry. Alleen extern transport gemockt. | Native tests geschreven, definitief bewijs vereist. |
| R39-04 | Per-dataset fouten en herstel; 401/429 en alle datasets mislukt blokkeren batch; 403 blijft ambigu. | Nieuwe tests, geschoonde overgangslogging en eigenaarstest. |
| R39-05 | Alleen bij requestaanvang en ontvangst gesloten kwartieren; receipt timestamp; voorlopige 30-minutengrens, geen cachepromotie. | Offline grens-/kloktests, publicatielatency blijft open. |
| R39-06 | Exacte checkout, lokale wheelhash/bytes/importlocatie, no-index/no-cache/offline, aparte config en skip-pip-start, rollback. | Native requirements-installatie plus preflight en negatieve hashtest in CI; echte launcherstart blijft eigenaarstest. |
| R39-07 | Eén currentcoordinator, gereserveerde IDs behouden, key-formatvalidatie gecentraliseerd. | Definitieve CI vereist. |
| R39-08 | Quality Scale-matrix met criteria uit Core 2026.11.3, beide talen, backlog, plan, contractreferentie en kennisupdate. | Geen Platinum- of faseclaim; open criteria blijven todo. |

Zie de [native lifecycle-tests](../tests/integration/test_lifecycle.py), [Quality Scale](../custom_components/nationaal_energie_dashboard/quality_scale.yaml) en [NL](user/nl/alpha-test.md)/[EN](user/en/alpha-test.md) installatie-instructies. Upstream basis: [Core sessiefactory](https://github.com/home-assistant/core/blob/2026.11.3/homeassistant/helpers/aiohttp_client.py), [aiohttp retrygedrag](https://github.com/aio-libs/aiohttp/blob/v3.14.5/aiohttp/client.py#L738-L742), [Core Quality Scale regels](https://github.com/home-assistant/core/blob/2026.11.3/script/hassfest/quality_scale.py). Definitieve exacte-commit CI moet opnieuw worden gecontroleerd. BL-003, BL-015 en BL-016 blijven open.

## Tussentijdse CI

De [Python-next-smoke](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45521339110) op f88347e slaagde met 150/150 zelfstandige tests. Formatter, lint, Gitleaks en Pylint waren groen in [Baseline 45521339121](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45521339121/job/138893677234); mypy meldde twee stale enum-type-narrowingfouten in lifecycle-tests, gecorrigeerd met een getypeerde asserthelper. Geen uitzondering of kwaliteitsverlaging. Nieuwe definitieve CI blijft vereist.
