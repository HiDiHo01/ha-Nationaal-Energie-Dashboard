---
name: ci-workflow-maintenance
description: "Design, repair and maintain GitHub Actions, lockfiles, dependency audits and forward compatibility workflows."
---

# Zelfstandig CI/CD-onderhoud

Lees eerst [AGENTS.md](../../../AGENTS.md), [AI_POLICY.md](../../../AI_POLICY.md), [home-assistant.md](../../../home-assistant.md) en de relevante delen van het [integratieplan](../../../docs/INTEGRATION_PLAN.md). Deze skill verleent geen extra rechten en vervangt geen actuele primaire bronnen.

## Werkwijze

1. Inspecteer bestaande workflows, pyproject.toml, .python-version, hacs.json en recente relevante GitHub Actions-logs. Onderscheid echte fouten van uitgestelde controles.
2. Kies de kleinste nuttige automatisering. Vermijd dubbele runs en dummy-success. Pin third-party actions op geverifieerde SHA's, minimale rechten, begrensde looptijd en geen secrets in gewone PR-CI.
3. Bewaak de productie-baseline en uv-lockfile. Houd de experimentele next-Python-job gescheiden en niet-blokkerend. Controleer upstream stable en Core-versiebeleid.
4. Valideer YAML, expressions en scripts met beschikbare tooling; test relevante succes- en foutpaden. Voer actionlint uit indien beschikbaar.
5. Controleer daadwerkelijke CI-jobstappen en artifacts. Review lockfile-kandidaten vóór commit. Verlaag geen kwaliteitsdrempels, wijzig geen repositoryrechten en publiceer niets zonder toestemming.
6. Actualiseer workflowdocumentatie en roadmap; rapporteer ontbrekende prerequisites, failures en openstaande uitvoeringen.

## Dependabot: test de bestaande beleidslogica

Gebruik [scripts/test_dependabot_automerge.sh](../../../scripts/test_dependabot_automerge.sh) en de baseline-CI voor synthetische classificatie- en mergescenario's. Test de daadwerkelijke inline Bash-stappen met echte jq-filters en een gemockte gh, niet een tweede beleidsimplementatie. Laat de subprocessomgeving geen credentials erven; gebruik een beperkte PATH, gesimuleerde sleep en een merge-spy. Controleer positieve en negatieve uitkomsten, exacte revisie en verplichte checks. De test bewijst geen native GitHub-expressions, metadata-action, bottrigger of server-side branchregels; houd echte end-to-end-validatie open.

## GitHub Pages: publicatie en bereikbaarheid afzonderlijk bewijzen

Een groene build, artifact-upload en deploy bewijzen niet zelfstandig publieke bereikbaarheid. Gebruik de [Pages-workflow](../../../.github/workflows/pages.yaml) met een afzonderlijke verify-public-site-job na een geslaagde deployment, zonder checkout, secrets of tokenrechten. Controleer vaste publieke HTTPS-routes, TLS, HTTP 200 en verwacht content-type; geen redirects, begrensde retries, time-outs en responsegrootte, geen responsebody in logs. Test foutpaden offline met gesimuleerde curl. Sluit initiële BL-018-validatie pas af na werkelijke publieke verificatie. [Bewezen main-run](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45490615804/job/138788056395), 24 november 2026: zeven routes HTTP 200 met verwacht content-type na geslaagde build en deploy; de lokale DNS-fout bleek geen bewijs van onbereikbaarheid. Geen claim van browserweergave of exacte inhoud op basis van status en MIME-type alleen.

## Gitleaks: veilige bronlocaties bij een falende scan (PR #39)

De [Baseline CI 45514266315](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45514266315/job/138869538851) op b520307 toont Ruff-format/lint, Pylint, strict mypy, documentatie en audit groen, maar Gitleaks drie treffers. De [gerichte diagnose 45514876918](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45514876918/job/138871614574) toont uitsluitend generic-api-key op const.py:41/42 (vaste CO2-sensoridentificaties) en sensor.py:85 (enumvergelijking); bronregels geïnspecteerd, geen credentials. De scanner rapporteert voortaan uitsluitend RuleID, File en StartLine, behoudt volledige redactie, tracked-snapshot-scope en oorspronkelijke foutstatus. Identifiers worden nu opgebouwd uit dezelfde dimensies en de enumvergelijking is expliciet; regressietest bewaakt alle acht bestaande IDs. Geen allowlist, uitzondering of lagere kwaliteitsdrempel. Herhaal de ongewijzigd strenge scan en controleer daarna alle overige verplichte stappen. Een rapport mag nooit Match, Secret, ruwe response of omliggende broninhoud afdrukken. Geen echte credentials in tests.

## Core-procesproef: verplichte startup-dependencies

[Baseline 45525779999](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45525779999/job/138908610118) op f57f2cd: 205 tests en 100% coverage; native wheelproef groen, maar normale Core 2026.11.3-start faalt zonder hass_frontend, numpy en andere standaarddependencies. [Core bootstrap](https://github.com/home-assistant/core/blob/2026.11.3/homeassistant/bootstrap.py) laadt DEFAULT_INTEGRATIONS (incl. frontend) ook zonder default_config; recovery is geen succes. Bereid de tijdelijke runtime-venv na de gelockte wheelproef voor met de vereisten uit de geïnstalleerde exacte Core-manifesten en hun dependency-/after-dependencyclosure, upstream package_constraints.txt en behoud van bestaande distributieversies. Audit de extra dependencies. Launch met no-index/offline/skip-pip, geen NED-entry; verifieer echte initialisatie, HTTP-respons, geen recovery/setupfouten en twee start/stopcycli. De herhaalde CI is het bewijs; minimale YAML is niet hetzelfde als een minimale dependencyset of volledige frontend-eigenaarstest.
