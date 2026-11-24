# Nationaal Energie Dashboard voor Home Assistant

Krijg inzicht en maak bewuste keuzes met historische, actuele en voorspellende energiedata.

Dit project ontwikkelt een custom integratie voor [Home Assistant](https://www.home-assistant.io/) op basis van de API van het [Nationaal Energie Dashboard (NED)](https://ned.nl/). Het doel is Nederlandse energiedata beschikbaar te maken voor sensoren, dashboards en automatiseringen in Home Assistant.

> **Ontwikkelstatus:** dit project bevindt zich in de initiële ontwikkelfase. Er is nog geen werkende integratie of installeerbare release beschikbaar.

## Energiedata

De NED API biedt onder meer de volgende gegevens. Ondersteuning door de Home Assistant-integratie moet nog worden geïmplementeerd.

| Gegevens | Beschrijving |
| --- | --- |
| Elektriciteitsproductie | Nederlandse opwek, zowel totaal als per energiedrager |
| Zonne-energie | Actuele en historische gegevens en voorspellingen |
| Windenergie | Gegevens en voorspellingen voor wind op land en op zee |
| Gas | Gasafzet en voorspellingen voor huishoudens en kleine bedrijven |
| CO₂ | Emissies en emissiefactoren |
| Historische gegevens | Voor bepaalde energiedragers beschikbaar vanaf 2016 |
| Voorspellingen | Voor geselecteerde datasets tot een week vooruit |

Afhankelijk van de dataset zijn intervallen van 10 minuten, 15 minuten, een uur, een dag, een maand of een jaar beschikbaar. De API biedt onder andere vermogen (kW), energie (kWh), CO₂-emissies (kg) en emissiefactoren (kg CO₂/kWh).

## Beoogde functionaliteit

- Configuratie via de Home Assistant-gebruikersinterface.
- Selecteerbare energiegegevens en sensoren.
- Historische, actuele en voorspelde energiedata, voor zover ondersteund door de API.
- Correcte eenheden, tijdzonebewuste tijdstempels en passende sensorclassificaties.
- Gebruik van energiedata in dashboards en automatiseringen.
- Installatie via HACS.

## API-sleutel

Voor toegang tot de NED API is een persoonlijke API-sleutel vereist.

1. Maak een account aan op [ned.nl](https://ned.nl/).
2. Open **Mijn account** en ga naar het tabblad **API**.
3. Genereer een API-sleutel.
4. Bewaar deze veilig voor de toekomstige configuratie van de integratie.

Het actuele API-basisadres is `https://api.ned.nl/v1`. Deel API-sleutels nooit via GitHub-issues, commits of diagnostische gegevens.

## Installatie en configuratie

Installatie via HACS en handmatige installatie worden beoogd. Zodra een werkende release beschikbaar is, worden hier de installatieprocedure, minimale Home Assistant-versie, configuratieopties en ondersteunde entiteiten beschreven.

## Ontwikkeling en kwaliteit

Het ontwikkeldoel is een onderhoudbare integratie die voldoet aan de toepasselijke criteria van de [Home Assistant Integration Quality Scale](https://contributors.home-assistant.io/core/quality-scale/), met Platinum als streefniveau. Dit is geen reeds behaalde of officieel toegekende kwalificatie.

Technische uitgangspunten:

- Python 3.14, afgestemd op de ondersteunde Home Assistant-versies.
- Asynchrone API-communicatie met hergebruik van de Home Assistant-websessie.
- Centrale gegevenscoördinatie en API-bewuste polling.
- Strikte typeannotaties, invoervalidatie en consistente foutafhandeling.
- Veilige herauthenticatie, herconfiguratie en diagnostiek zonder gevoelige gegevens.
- Geautomatiseerde tests, linting, typecontrole en CI-validatie.

## Roadmap

- [ ] Repositorystructuur en ontwikkelrichtlijnen vastleggen.
- [ ] NED API-client en datamodellen implementeren.
- [ ] Configuratieflow en gegevenscoördinator implementeren.
- [ ] Sensoren en voorspellingen beschikbaar maken.
- [ ] Vertalingen, diagnostiek en foutafhandeling toevoegen.
- [ ] Tests en GitHub Actions inrichten.
- [ ] HACS-compatibiliteit realiseren.
- [ ] Eerste release publiceren en toepasselijke kwaliteitscriteria valideren.

## Ondersteuning en bijdragen

Meld fouten en functievoorstellen via [GitHub Issues](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/issues). Vermeld waar relevant de Home Assistant-versie, integratieversie en stappen om het probleem te reproduceren. Verwijder persoonlijke gegevens en API-sleutels uit logbestanden.

## Referenties

- [Nationaal Energie Dashboard](https://ned.nl/)
- [Officiële NED API-documentatie, handleiding en datacatalogus](https://ned.nl/nl/api)
- [NED API](https://api.ned.nl/v1)
- [Home Assistant](https://www.home-assistant.io/)
- [Home Assistant Integration Quality Scale](https://contributors.home-assistant.io/core/quality-scale/)
- [HACS](https://www.hacs.xyz/)

## Disclaimer

Dit is een onafhankelijk communityproject en geen officiële integratie van het Nationaal Energie Dashboard of Home Assistant. De beschikbaarheid, actualiteit en nauwkeurigheid van energiedata zijn afhankelijk van de bron en de betreffende dataset.
