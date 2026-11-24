# Ontwikkeling

Lees eerst [AGENTS.md](../AGENTS.md), [AI_POLICY.md](../AI_POLICY.md) en het [integratieplan](INTEGRATION_PLAN.md). Gebruik de Python-versie van de vastgelegde stabiele Home Assistant Core-baseline.

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
