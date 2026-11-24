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
