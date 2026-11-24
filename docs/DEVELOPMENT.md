# Ontwikkeling

Lees eerst [AGENTS.md](../AGENTS.md), [AI_POLICY.md](../AI_POLICY.md) en het [integratieplan](INTEGRATION_PLAN.md). Gebruik Python 3.14 voor zover compatibel met de ondersteunde Home Assistant-versie.

## Compatibiliteitsbaseline

De minimale ondersteunde Home Assistant Core-versie is bij iedere nieuwe integratierelease de dan nieuwste stabiele Core-release, inclusief patchnummer. Controleer deze via https://version.home-assistant.io/stable.json en de officiële release-informatie. Gebruik een expliciete versie per release in hacs.json (homeassistant), documentatie en de reproduceerbare testomgeving; verhoog de grens pas voor een nieuwe integratierelease, niet met terugwerkende kracht. Oudere Core-versies, beta's en developmentversies hoeven niet ondersteund te worden. Valideer vóór publicatie installatie en tests tegen de vastgelegde baseline.

Huidige minimumversie: 2026.11.3. Pin deze versie in de nog te configureren ontwikkel- en testomgeving. Python 3.14 is de doelversie; verifieer compatibiliteit van de runtime en testdependencies voordat de tooling als gereed wordt gemarkeerd.

De projecttooling, dependencies, testcommando's en CI worden in fase 0 definitief ingericht. De huidige structuur bevat geen uitvoerbare integratie of tests. Maak geen publieke releases zonder toestemming.
