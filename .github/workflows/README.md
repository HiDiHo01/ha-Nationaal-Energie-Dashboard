# CI/CD

| Workflow | Trigger | Doel |
| --- | --- | --- |
| [ci.yaml](ci.yaml) | Push, PR, handmatig | Exacte Python/Core-baseline, uv-lockfile, dependency-installatie, linting, strict typing, offline tests, coverage en pip-audit |
| [python-next-smoke.yaml](python-next-smoke.yaml) | Push, PR, handmatig | Niet-blokkerende volgende Python-generatie, zelfstandige API-library |
| [hassfest.yaml](hassfest.yaml) | Push, PR, handmatig | Officiële Hassfest-validatie zodra manifest bestaat |
| [hacs.yaml](hacs.yaml) | Handmatig, gepubliceerde release | Marketplace-validatie zonder genegeerde checks |
| [baseline-watch.yaml](baseline-watch.yaml) | Dagelijks 07:17 UTC, handmatig | Signaleer afwijkende Core-stablebaseline |
| [Dependabot](../dependabot.yml) | Wekelijks | Updatevoorstellen voor GitHub Actions |

Alle workflows gebruiken alleen leesrechten en geen NED API-key. Lockfile-kandidaten zijn tijdelijk beschikbaar als artifact; review en commit ze vóór implementatie-CI. Afwezige broncode of metadata wordt expliciet gemeld en vormt geen bewijs van geslaagde inhoudelijke tests. Handmatige Hassfest en Marketplace-validatie vereisen de relevante integratiebestanden. HACS en Hassfest gebruiken upstream containerimages met veranderlijke tags. De Python-next-job blijft niet-blokkerend.

Gepland wanneer de prerequisites bestaan: api-contract.yaml (opt-in met secrets) en release.yaml (build/releasevalidatie zonder automatische publicatie). Geen automatische merges, releases of externe packagepublicaties. Zie [AGENTS.md](../../AGENTS.md) en [integratieplan](../../docs/INTEGRATION_PLAN.md).
