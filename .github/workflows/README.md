# CI/CD

Geplande workflows: ci.yaml (lint, typecontrole, tests en security), hassfest.yaml, hacs.yaml, api-contract.yaml (opt-in met secrets) en release.yaml (build en geautoriseerde publicatie). Activeer deze wanneer hun prerequisites bestaan. Geen dummy-controles of automatische ongeautoriseerde publicaties. Zie [AGENTS.md](../../AGENTS.md).

Actief ingericht: [python-next-smoke.yaml](python-next-smoke.yaml). Experimentele Python 3.15-job, niet releaseblokkerend, zonder Home Assistant-dependencies of API-secrets. Ontbrekende broncode en tests worden expliciet gerapporteerd. Zie [ontwikkelrichtlijnen](../../AGENTS.md). De verplichte baseline-CI blijft een afzonderlijke geplande workflow.
