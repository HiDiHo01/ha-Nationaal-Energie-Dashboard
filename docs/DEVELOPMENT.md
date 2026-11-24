# Ontwikkeling

Lees eerst [AGENTS.md](../AGENTS.md), [AI_POLICY.md](../AI_POLICY.md) en het [integratieplan](INTEGRATION_PLAN.md). Gebruik de Python-versie van de vastgelegde stabiele Home Assistant Core-baseline.

## Compatibiliteitsbaseline

De minimale ondersteunde Home Assistant Core-versie is bij iedere nieuwe integratierelease de dan nieuwste stabiele Core-release, inclusief patchnummer. Controleer deze via https://version.home-assistant.io/stable.json en de officiële release-informatie. Gebruik een expliciete versie per release in hacs.json (homeassistant), documentatie en de reproduceerbare testomgeving; verhoog de grens pas voor een nieuwe integratierelease, niet met terugwerkende kracht. Oudere Core-versies, beta's en developmentversies hoeven niet ondersteund te worden. Valideer vóór publicatie installatie en tests tegen de vastgelegde baseline.

Huidige minimumversie: 2026.11.3. Pin deze versie in de nog te configureren ontwikkel- en testomgeving. De Python-doelversie volgt de major.minor-versie die de nieuwste stabiele Home Assistant Core-release gebruikt. Controleer bij het vaststellen van de Core-baseline de officiële release-tag: pyproject.toml (requires-python en toolversies) en .python-version (exacte ontwikkelversie). Neem de officiële minimale Python-versie over en pin de ontwikkelomgeving op de bijbehorende exacte Python-versie. Gebruik dezelfde major.minor-versie voor Ruff, Pylint, mypy en CI. Herbeoordeel deze waarden bij elke nieuwe integratierelease; pas oudere releases niet met terugwerkende kracht aan. Kies nooit zelfstandig een nieuwere Python-generatie dan de vastgelegde Core-baseline.

Baseline 24 november 2026: Home Assistant Core 2026.11.3, Python 3.14, upstream requires-python >=3.14.2 en ontwikkelversie 3.14.10. Bronnen: [Core pyproject.toml](https://github.com/home-assistant/core/blob/2026.11.3/pyproject.toml) en [Core .python-version](https://github.com/home-assistant/core/blob/2026.11.3/.python-version).

De repository bevat een .python-version met de exacte ontwikkelpin. Verifieer compatibiliteit van runtime en testdependencies voordat de tooling als gereed wordt gemarkeerd.

De projecttooling, dependencies, testcommando's en CI worden in fase 0 definitief ingericht. De huidige structuur bevat geen uitvoerbare integratie of tests. Maak geen publieke releases zonder toestemming.
