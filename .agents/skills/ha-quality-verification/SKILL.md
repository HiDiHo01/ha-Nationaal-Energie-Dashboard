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

- Formatteer ook alle gewijzigde test- en maintenancebestanden; handmatig afgebroken Query- en assertEqual-aanroepen zijn twee bewezen regressies. Laat de gelockte formatter beslissen, ook bij regels die onder de limiet passen. Voer de formatcheck uit op de definitieve inhoud na de laatste Python-wijziging; herhaal deze na iedere latere codewijziging. Een succesvolle unittest-run, syntaxiscontrole of handmatige lengtemeting vervangt de formatter niet.
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

### Bewezen regressie — PR #21, 24 november 2026

Baseline: Core 2026.11.3, Python 3.14.10, Ruff 0.17.6, line-length 88. [Falende Baseline CI](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45484642366/job/138766646265): hook ruff-format, exitcode 1, scripts/test_ned_contract_extended.py:269. Ruff-lint, Pylint maintenance, strict mypy maintenance, documentatie, offline tests en dependency-audit waren geslaagd. Het betrof geen inhoudelijke testfout. Ruff wilde uitsluitend de volgende wijziging:

```diff
-        self.assertEqual(
-            [query.type_id for query in suite], [1, 2, 51, 27, 59, 27]
-        )
+        self.assertEqual([query.type_id for query in suite], [1, 2, 51, 27, 59, 27])
```

[Herstelcommit 4a0bca6](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/commit/4a0bca648e68e50587a62f1d951df098cd50d0be): exacte CI-diff zonder testlogica, productiecode, lockfile of kwaliteitsdrempel te wijzigen; contractreferentie en backlog bijgewerkt. De lokale gelockte Python-omgeving ontbrak. [Herhaalde Baseline CI](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45485551617/job/138769838010) is geslaagd, inclusief afzonderlijke Ruff-format- en Ruff-lint-hooks, Pylint, strict mypy, documentatievalidator, offline maintenance-tests, synthetische runtime-wheelproef en dependency-audit. Deze tweede formatterregressie bevestigt dat ook testbestanden de verplichte laatste formatcheck nodig hebben. Geen bewijs van live API-semantiek of native skillactivatie.

## Mypy: bronselectie bij gefaseerde implementatie

[PR #32, 24 november 2026](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45496510328/job/138808349344): strict mypy exitcode 2 (`There are no .py[i] files in directory 'custom_components/nationaal_energie_dashboard'`). Een expliciet opgegeven lege fase-placeholder is geen geldig afzonderlijk mypy-doel. Gebruik de centrale recursieve rootdoelselectie (`files = ["."]`, `exclude_gitignore = true`) met behoud van `strict = true`, `mypy_path` en bestaande Python-baseline. Hiermee blijven bestaande en toekomstige Python-bronnen onder controle zonder lege modules toe te voegen of de integratie uit de scope te verwijderen. Een lege glob is geen veilige workaround: mypy behoudt een niet-matchend globpatroon als invoerpad. Zie de [mypy-bronselectie](https://mypy.readthedocs.io/en/stable/running_mypy.html) en [configuratiereferentie](https://mypy.readthedocs.io/en/stable/config_file.html). Controleer de daadwerkelijke herhaalde CI, inclusief mypy, pytest, coverage en wheelinstallatie; geen geslaagde status voordat bewijs beschikbaar is.

```diff
- files = ["custom_components/nationaal_energie_dashboard", "packages/ned-api/src/ned_api", "tests"]
+ files = ["."]
+ exclude_gitignore = true
```

[Herhaalde Baseline CI](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45497802933/job/138812806119) op herstelcommit [b5b58f2](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/commit/b5b58f25cb99c4d5af9cfc793770c4c74c38f7ce) slaagde op Core 2026.11.3/Python 3.14.10, mypy 2.4.1: strict mypy, negen API-tests (pytest 9.0.3), 100% coverage van 11 statements zonder aanwezige branches, zelfstandige typed wheelbouw en geïsoleerde installatie, 23 synthetische Dependabot-scenario's, synthetische native HA-runtimeproef en dependency-audit zonder bekende kwetsbaarheden. Vijf upstream DeprecationWarnings (Home Assistant web.Application-overerving en backoff asyncio.iscoroutinefunction); geen waarschuwingen onderdrukt. Geen bewijs van volledige integratie of toekomstige branchcoverage.

Preventie: controleer bij elke faseovergang de werkelijke Python-bronstructuur en de mypy-doelselectie. Draai vanuit de repositoryroot `uv run --locked mypy` en daarna de volledige pre-commit-controles; behoud strict-modus en controleer dat nieuwe modules binnen de scope vallen. Geen dummybestanden, handmatige uitsluiting van integratiebronnen of versoepeling van de kwaliteitsdrempels.
