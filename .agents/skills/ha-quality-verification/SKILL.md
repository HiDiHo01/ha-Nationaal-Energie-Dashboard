---
name: ha-quality-verification
description: "Verify Python and Home Assistant code changes with Ruff, Pylint, strict mypy, pytest, coverage, security and Quality Scale evidence."
---

# Kwaliteitsverificatie

Lees eerst [AGENTS.md](../../../AGENTS.md), [AI_POLICY.md](../../../AI_POLICY.md), [home-assistant.md](../../../home-assistant.md) en de relevante delen van het [integratieplan](../../../docs/INTEGRATION_PLAN.md). Deze skill verleent geen extra rechten en vervangt geen actuele primaire bronnen.

## Werkwijze

1. Lees AGENTS.md, home-assistant.md en pyproject.toml. Controleer .python-version, hacs.json en de geïnstalleerde baseline.
2. Draai relevante gerichte tests, daarna toepasselijke formattering, lint, strict mypy en offline pytest volgens AGENTS.md; volg de Ruff-formatprocedure hieronder. Gebruik de gelockte omgeving wanneer beschikbaar.
3. Controleer de gecombineerde coveragepoort, afzonderlijke branchcoverage en modulegrenzen. Verlaag geen thresholds; meld ontbrekende modules of tests als niet uitgevoerd.
4. Controleer documentatie-impact, beide gebruikersdocumentatietalen en de NL/EN-vertalingen. Draai de documentatievalidator en regressietests en controleer de inhoudelijke juistheid en native vertaling tijdens integratietests zodra beschikbaar.
5. Controleer async I/O, cancellation, gedeelde sessies, credentialredactie, uitzonderingen, vertalingen, registry-stabiliteit en regressies.
6. Gebruik officiële Quality Scale-criteria; koppel done aan concrete tests en code, motiveer vrijstellingen, laat onbewezen criteria open. Platinum is een doel, geen certificering.
7. Rapporteer commando's, exitstatus, aantallen, coverage, CI-run en beperkingen. Corrigeer relevante fouten en herhaal controles.

## Ruff-format: preventie en herstel van een falende required check

- Formatter en lint zijn afzonderlijke controles. Geslaagde tests, compileall of `ruff check` bewijzen niet dat `ruff format --check` slaagt. Gebruik de Ruff-versie uit de gecommitteerde uv.lock en de centrale pyproject.toml; geen globale of willekeurig nieuwere formatter.
- Formatteer gewijzigde Python-bestanden vanuit de repositoryroot vóór commit met `uv run --locked ruff format <gewijzigde-pythonbestanden>` (vervang de placeholder door de concrete paden). Draai vervolgens:

  ```bash
  uv run --locked ruff format --check .
  uv run --locked ruff check .
  uv run --locked pre-commit run --all-files --show-diff-on-failure
  ```

- Inspecteer de diff na formattering en herhaal relevante offline tests. Controleer na commit dat de daadwerkelijk gepushte inhoud overeenkomt met de gecontroleerde bestanden. Houd formatteringswijzigingen gericht; pas geen businesslogica, configuratie, lockfile of kwaliteitsdrempels aan om een formatteringsfout te omzeilen.
- Bij falende CI: lees de exacte joblog, hook-ID `ruff-format`, exitcode, bestandslocatie en voorgestelde formatterdiff. Kan de gelockte omgeving lokaal niet worden uitgevoerd, pas uitsluitend de expliciete CI-formatterdiff toe en vermeld de lokale beperking. Verifieer op de nieuwe commit dat de verplichte Baseline CI én de Ruff-format-hook slagen; beschouw de fix vóór dat bewijs als onbevestigd. Gebruik [ci-workflow-maintenance](../ci-workflow-maintenance/SKILL.md) voor CI-diagnose.

### Bewezen regressie — PR #16, 24 november 2026

Baseline: Python 3.14, Ruff 0.17.6, line-length 88. [Falende CI](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45476735384/job/138738811527) meldde exitcode 1 voor `scripts/ned_contract_extended.py:140`: een korte, handmatig afgebroken `Query(...)` moest op één regel. De [herstelcommit](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/commit/a2f9c510d64e33eb51eba113a56b6399b86c0671) nam de exacte CI-diff over:

```diff
-            Query(
-                type_id=2, classification=2, day=date(2026, 11, 22), granularity=6
-            ),
+            Query(type_id=2, classification=2, day=date(2026, 11, 22), granularity=6),
```

De [herhaalde Baseline CI](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45477494450/job/138741477108) slaagde; de logs bevestigen afzonderlijk Ruff-format en Ruff-lint. Dit bewijst de formatteringsfix op die commit, niet de live API-semantiek of native skillactivatie. Laat bij toekomstige codewijzigingen Ruff zelf de regelindeling bepalen.
