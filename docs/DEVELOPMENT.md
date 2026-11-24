# Ontwikkeling

Lees eerst [AGENTS.md](../AGENTS.md), [AI_POLICY.md](../AI_POLICY.md) en het [integratieplan](INTEGRATION_PLAN.md). Gebruik de Python-versie van de vastgelegde stabiele Home Assistant Core-baseline.

## Skills en Home Assistant-referentie

Lees [home-assistant.md](../home-assistant.md) bij Home Assistant-werkzaamheden. Gebruik de relevante [repositoryskills](../.agents/skills/README.md) door hun SKILL.md te lezen; Codex-omgevingen die repositoryskills ondersteunen kunnen ze ook automatisch ontdekken. Onderhoud beide proactief volgens AGENTS.md §1.1. De initiële skillstructuur is documentatie; daadwerkelijke selectie en effectiviteit in implementatietaken moeten nog worden geverifieerd.

## Compatibiliteitsbaseline

De minimale ondersteunde Home Assistant Core-versie is bij iedere nieuwe integratierelease de dan nieuwste stabiele Core-release, inclusief patchnummer. Controleer deze via https://version.home-assistant.io/stable.json en de officiële release-informatie. Gebruik een expliciete versie per release in hacs.json (homeassistant), documentatie en de reproduceerbare testomgeving; verhoog de grens pas voor een nieuwe integratierelease, niet met terugwerkende kracht. Oudere Core-versies, beta's en developmentversies hoeven niet ondersteund te worden. Valideer vóór publicatie installatie en tests tegen de vastgelegde baseline.

Huidige minimumversie: 2026.11.3. Pin deze versie in de nog te configureren ontwikkel- en testomgeving. De Python-doelversie volgt de major.minor-versie die de nieuwste stabiele Home Assistant Core-release gebruikt. Controleer bij het vaststellen van de Core-baseline de officiële release-tag: pyproject.toml (requires-python en toolversies) en .python-version (exacte ontwikkelversie). Neem de officiële minimale Python-versie over en pin de ontwikkelomgeving op de bijbehorende exacte Python-versie. Gebruik dezelfde major.minor-versie voor Ruff, Pylint, mypy en CI. Herbeoordeel deze waarden bij elke nieuwe integratierelease; pas oudere releases niet met terugwerkende kracht aan. Kies nooit zelfstandig een nieuwere Python-generatie dan de vastgelegde Core-baseline.

Baseline 24 november 2026: Home Assistant Core 2026.11.3, Python 3.14, upstream requires-python >=3.14.2 en ontwikkelversie 3.14.10. Bronnen: [Core pyproject.toml](https://github.com/home-assistant/core/blob/2026.11.3/pyproject.toml) en [Core .python-version](https://github.com/home-assistant/core/blob/2026.11.3/.python-version).

De repository bevat een .python-version met de exacte ontwikkelpin. Verifieer compatibiliteit van runtime en testdependencies voordat de tooling als gereed wordt gemarkeerd.

## Centrale tooling

[pyproject.toml](../pyproject.toml) bevat de projectmetadata, dev-dependencygroep en configuratie voor Ruff, Pylint, strict mypy, pytest en coverage. De root is een ontwikkelworkspace, geen distributiepackage. Versie 0.0.0 is uitsluitend de metadata van de nog niet uitgebrachte workspace. De runtime-library krijgt eigen buildmetadata in fase 1.

De officiële [pytest-homeassistant](https://pypi.org/project/pytest-homeassistant/2026.11.3/) testplugin volgt Core 2026.11.3; combineer deze niet met pytest-homeassistant-custom-component. Gebruik uv met de exacte .python-version. Volgende stap: resolveer en commit uv.lock en verifieer de volledige ontwikkelinstallatie. Er is nog geen gevalideerde lockfile.

Na installatie van de ontwikkelomgeving en implementatie van de broncode:

```bash
ruff format --check .
ruff check .
pylint custom_components/nationaal_energie_dashboard
pylint packages/ned-api/src/ned_api
mypy
pytest --cov --cov-branch --cov-report=term-missing
pip-audit
```

De coverage-drempel bedraagt 95% voor de gecombineerde lijn- en branchdekking; de afzonderlijke branch- en modulecoverage-doelen uit het integratieplan worden aanvullend in CI bewaakt. Live contracttests zijn standaard uitgesloten. Gebruik uitsluitend voor een geautoriseerde live test `pytest -m live_api` met veilig geïnjecteerde credentials.

De TOML-syntaxis, versie-uitlijning en dependency-specifiers zijn statisch gevalideerd. Een geïsoleerde smoketest met synthetische testcode op Python 3.13.5 bevestigde async-testuitvoering, standaard uitsluiting van live_api en de 95%-coveragepoort. Dit is geen integratietest. Python 3.14.10 kon in de validatieomgeving niet worden geïnstalleerd; volledige dependencyresolutie, tooluitvoering en runtimevalidatie staan nog open.

De huidige structuur bevat geen uitvoerbare integratie of repositorytests. Maak geen publieke releases zonder toestemming.

## Forward Compatibility Testing

- De Home Assistant/Python-baseline blijft leidend voor productiecode, linting, strict typing, volledige integratietests en de verplichte coveragepoorten.
- Onderhoud de afzonderlijke workflow python-next-smoke.yaml voor de eerstvolgende Python-major.minor-generatie (momenteel 3.15, productie 3.14). Deze experimentele job is niet releaseblokkerend (continue-on-error: true); failures blijven zichtbaar in de jobdetails. Bij een Core/Python-upgrade schuift de experimentele versie mee. Introduceer geen next-only syntax in productiecode.
- Draai op push, pull request en workflow_dispatch met alleen contents: read, zonder API-secrets of installatie van Home Assistant/het root-dev-dependencygroup.
- Controleer de volgende-versierelatie met .python-version, compileer aanwezige Python-bronnen, installeer de zelfstandige ned_api-library vanuit packages/ned-api, voer pip check en een import uit en draai offline tests/api zonder de root-coveragepoort.
- Voeg in fase 1 een zelfstandige test-extra toe aan packages/ned-api/pyproject.toml (pytest, pytest-asyncio en alle vereiste API-testdependencies, geen Home Assistant). API-tests en fixtures zijn onafhankelijk van Home Assistant; plaats noodzakelijke conftest-fixtures onder tests/api. Sluit live_api-tests uit.
- Zolang broncode of tests ontbreken, rapporteert de workflow expliciet welke controles niet zijn uitgevoerd. Een groene experimentele job is geen bewijs van volledige runtimecompatibiliteit of Platinum.

De workflow is opgeslagen in [python-next-smoke.yaml](../.github/workflows/python-next-smoke.yaml). YAML-structuur en Bash-syntaxis zijn lokaal gecontroleerd; de no-source-paden, succesvolle en mislukte syntaxcompilatie en afwijzing van een verkeerde versiebaseline zijn met synthetische bestanden en Python 3.13.5 getest. Dit is geen uitvoering op Python 3.15. De volledige GitHub Actions-run en librarytests moeten nog worden geverifieerd.

## GitHub Actions

- Baseline CI (ci.yaml) installeert de exacte .python-version, controleert de Core- en toolversies, gebruikt uv 0.13.9 en valideert dependencies. Zolang uv.lock ontbreekt, wordt een lockfile-kandidaat als tijdelijk workflow-artifact aangeboden. Review en commit die vóór implementatie-CI; bij aanwezige Python-broncode is een ontbrekende lockfile een fout. Voeg de zelfstandige API-library met testdependencies toe aan de gelockte ontwikkelomgeving zodra deze beschikbaar is.
- Baseline CI bewaakt Ruff, Pylint, strict mypy, offline pytest, de gecombineerde coveragepoort, de afzonderlijke totale branchcoverage en de huidige modulecategorieën. Pas de coveragecontrole aan wanneer forecastberekeningen of andere kritieke modules andere bestandsnamen krijgen. Dependency-audit draait met pip-audit; kwetsbaarheden mogen niet stilzwijgend worden onderdrukt.
- Hassfest draait automatisch zodra het manifest aanwezig is; vóór dat moment wordt de ontbrekende validatie expliciet gemeld. Handmatige Hassfest-validatie vereist een manifest. Marketplace-validatie (hacs.yaml) draait handmatig en na een geautoriseerde gepubliceerde release, zonder genegeerde HACS-checks of PR-commentaar. Een echte succesvolle validatie is vereist vóór catalogusaanmelding.
- Baseline-watch controleert dagelijks de officiële Core-stablefeed en meldt afwijkingen zonder automatisch de versiegrens te wijzigen. Controleer bij de volgende release ook het upstream Python-contract. Dependabot stelt wekelijks updates voor GitHub Actions voor, zonder automatische merge.
- Gebruik standaard contents: read, vastgepinde action-SHA's, geen persistente checkoutcredentials en geen secrets in gewone CI. Upstream Hassfest/HACS-actions gebruiken zelf containerimages met veranderlijke tags; de action-SHA alleen maakt hun uitvoering niet volledig reproduceerbaar.
- De experimentele Python-next-job blijft afzonderlijk en niet-blokkerend. Geen automatische releases, packagepublicaties of live contractrequests. Voeg api-contract.yaml en releasevalidatie pas toe wanneer testcontract, veilige secret-injectie, distributiemethode en buildvereisten concreet beschikbaar zijn.

De vier nieuwe workflowbestanden en Dependabot-configuratie zijn lokaal als YAML geparseerd. Bash-syntaxis, ingebedde Python-syntaxis, SHA-lengtes, ontbrekende-code/lockfile-paden, Hassfest-readiness, coveragegrenzen en versieveroudering zijn met synthetische fixtures gecontroleerd op Python 3.13.5. Er is nog geen bewijs van volledige baseline-CI op de GitHub-runner. De eerdere [Python-next-run](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45447217991) is geslaagd; zonder API-library zijn import- en API-tests niet uitgevoerd.
