# CI/CD

| Workflow | Trigger | Doel |
| --- | --- | --- |
| [ci.yaml](ci.yaml) | Push, PR, handmatig | Exacte Python/Core-baseline, uv-lockfile, dependency-installatie, pre-commit, secret-scan, linting, strict typing, offline tests, coverage, geïsoleerde runtime-wheelproef en pip-audit |
| [python-next-smoke.yaml](python-next-smoke.yaml) | Push, PR, handmatig | Niet-blokkerende volgende Python-generatie, zelfstandige API-library |
| [hassfest.yaml](hassfest.yaml) | Push, PR, handmatig | Officiële Hassfest-validatie zodra manifest bestaat |
| [hacs.yaml](hacs.yaml) | Handmatig, gepubliceerde release | Marketplace-validatie zonder genegeerde checks |
| [baseline-watch.yaml](baseline-watch.yaml) | Dagelijks 07:17 UTC, handmatig | Signaleer afwijkende Core-stablebaseline |
| [dependabot-automerge.yaml](dependabot-automerge.yaml) | Dependabot-PR naar main | Gecontroleerde squash-merge van geschikte minor/patchupdates na verplichte CI |
| [api-contract.yaml](api-contract.yaml) | Handmatig, main, expliciete bevestiging | Zes kwartiersemantiekverzoeken (semantics, standaard), twee dagaggregatieverzoeken (daily), zes tijdzoneverzoeken (timezone) of maximaal 18 read-only NED-requests (full) met beveiligde environment-secret; zie [API-contract](../../docs/API_REFERENCE.md) |
| [pages.yaml](pages.yaml) | PR, push naar main (sitewijzigingen), handmatig | Gelockte Jekyll-build, gem-audit, NL/EN- en linkvalidatie; uitsluitend main deployen via GitHub Pages |
| [Dependabot](../dependabot.yml) | Dagelijks | Update-PR's voor GitHub Actions, uv (directe/indirecte dependencies) pre-commit-hooks en Bundler |

Gewone CI gebruikt alleen leesrechten en geen NED API-key. De afzonderlijke Dependabot-mergejob heeft beperkte schrijfbevoegdheid; geen checkout, PR-code-uitvoering of extra secrets. De gecommitteerde lockfile is verplicht. Baseline CI gebruikt dezelfde pre-commit-hooks als lokaal; alleen de afzonderlijke tests en coverage volgen daarna. Afwezige broncode of metadata wordt expliciet gemeld en vormt geen bewijs van geslaagde inhoudelijke tests. Handmatige Hassfest en Marketplace-validatie vereisen de relevante integratiebestanden. HACS en Hassfest gebruiken upstream containerimages met veranderlijke tags. De Python-next-job blijft niet-blokkerend.

Gepland wanneer de prerequisites bestaan: release.yaml (build/releasevalidatie zonder automatische publicatie). Main is beschermd; geschikte Dependabot-updates worden automatisch verwerkt volgens AGENTS.md §13.3. De end-to-end-merge moet nog met een echte Dependabot-PR worden aangetoond. Core/pytest-homeassistant blijven gekoppeld aan de releasebaseline; controleer veiligheidsmeldingen ook via pip-audit. Voeg het API-packagemanifest toe zodra aanwezig; externe hookupdates vereisen afzonderlijke beoordeling. Geen automatische releases of externe packagepublicaties. Zie [AGENTS.md](../../AGENTS.md) en [integratieplan](../../docs/INTEGRATION_PLAN.md).

Pages bouwt uitsluitend site/ met gelockte Ruby/Bundler-dependencies; controleert een exacte uitvoerallowlist, taalwissel, interne links en gem-audit. De standaard root-Jekyll-workflow is vervangen. De deployjob heeft alleen pages: write en id-token: write, gebruikt github-pages en ontvangt geen NED-secret. Zie [ontwikkelreferentie](../../docs/DEVELOPMENT.md#github-pages).
