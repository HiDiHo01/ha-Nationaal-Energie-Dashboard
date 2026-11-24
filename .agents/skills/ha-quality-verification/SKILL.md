---
name: ha-quality-verification
description: "Verify Python and Home Assistant code changes with Ruff, Pylint, strict mypy, pytest, coverage, security and Quality Scale evidence."
---

# Kwaliteitsverificatie

Lees eerst [AGENTS.md](../../../AGENTS.md), [AI_POLICY.md](../../../AI_POLICY.md), [home-assistant.md](../../../home-assistant.md) en de relevante delen van het [integratieplan](../../../docs/INTEGRATION_PLAN.md). Deze skill verleent geen extra rechten en vervangt geen actuele primaire bronnen.

## Werkwijze

1. Lees AGENTS.md, home-assistant.md en pyproject.toml. Controleer .python-version, hacs.json en de geïnstalleerde baseline.
2. Draai relevante gerichte tests, daarna toepasselijke formattering, lint, strict mypy en offline pytest volgens AGENTS.md. Gebruik de gelockte omgeving wanneer beschikbaar.
3. Controleer de gecombineerde coveragepoort, afzonderlijke branchcoverage en modulegrenzen. Verlaag geen thresholds; meld ontbrekende modules of tests als niet uitgevoerd.
4. Controleer documentatie-impact, beide gebruikersdocumentatietalen en de NL/EN-vertalingen. Draai de documentatievalidator en regressietests en controleer de inhoudelijke juistheid en native vertaling tijdens integratietests zodra beschikbaar.
5. Controleer async I/O, cancellation, gedeelde sessies, credentialredactie, uitzonderingen, vertalingen, registry-stabiliteit en regressies.
6. Gebruik officiële Quality Scale-criteria; koppel done aan concrete tests en code, motiveer vrijstellingen, laat onbewezen criteria open. Platinum is een doel, geen certificering.
7. Rapporteer commando's, exitstatus, aantallen, coverage, CI-run en beperkingen. Corrigeer relevante fouten en herhaal controles.
