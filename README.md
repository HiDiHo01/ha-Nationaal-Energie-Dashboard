# Nationaal Energie Dashboard voor Home Assistant

Nederlands | [English](README.en.md)

Krijg inzicht en maak bewuste keuzes met historische, actuele en voorspellende energiedata.

Dit project ontwikkelt een custom integratie voor [Home Assistant](https://www.home-assistant.io/) op basis van de API van het [Nationaal Energie Dashboard (NED)](https://ned.nl/). Het doel is Nederlandse energiedata beschikbaar te maken voor sensoren, dashboards en automatiseringen in Home Assistant.

> **Ontwikkelstatus:** dit project bevindt zich in de initiële ontwikkelfase. Er is nog geen werkende integratie of installeerbare release beschikbaar.

## Energiedata

De NED API biedt volgens de bronbeschrijving onder meer de volgende gegevens. De exacte API-contracten en ondersteunde datasetcombinaties moeten nog worden gevalideerd; ondersteuning door de integratie moet nog worden geïmplementeerd.

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
- Opname in de algemene Home Assistant Marketplace-catalogus.

## API-sleutel

Voor toegang tot de NED API is een persoonlijke API-sleutel vereist.

1. Maak een account aan op [ned.nl](https://ned.nl/).
2. Open **Mijn account** en ga naar het tabblad **API**.
3. Genereer een API-sleutel.
4. Bewaar deze veilig voor de toekomstige configuratie van de integratie.

Het beoogde API-basisadres is `https://api.ned.nl/v1`. Deel API-sleutels nooit via GitHub-issues, commits of diagnostische gegevens.

## Installatie en configuratie

**Minimale Home Assistant Core-versie: 2026.11.3.** Per nieuwe integratierelease wordt de nieuwste stabiele Core-release als minimum gehanteerd. Oudere Core-versies en prereleases hoeven niet ondersteund te worden. De actuele baseline is een ontwikkeldoel, nog geen geteste compatibiliteitsclaim.

Het distributiedoel is Home Assistant Marketplace. Voor de [HACS-licentiecontrole](https://www.hacs.xyz/docs/publish/include/#check-license) is GPL-3.0-only gekozen, een OSI-goedgekeurde licentie. GitHub-licentieherkenning is bevestigd; daadwerkelijke catalogustoelating moet nog worden aangetoond. De runtime-distributiestrategie is gevalideerd met een synthetische wheel; volledige productie-installatie blijft open. Tijdens ontwikkeling wordt lokaal getest. Er is nog geen installeerbare release. Officieel aangeboden versies mogen volgens de gebruiksvoorwaarden binnen Home Assistant worden gebruikt.

## Ontwikkeling en kwaliteit

Het ontwikkeldoel is een onderhoudbare integratie die voldoet aan de toepasselijke criteria van de [Home Assistant Integration Quality Scale](https://contributors.home-assistant.io/core/quality-scale/), met Platinum als streefniveau. Dit is geen reeds behaalde of officieel toegekende kwalificatie.

Technische uitgangspunten:

- Python-doelversie volgt de nieuwste stabiele Home Assistant Core-release (momenteel Python 3.14; minimum 3.14.2, ontwikkelversie 3.14.10).
- Asynchrone API-communicatie met hergebruik van de Home Assistant-websessie.
- Centrale gegevenscoördinatie en API-bewuste polling.
- Strikte typeannotaties, invoervalidatie en consistente foutafhandeling.
- Veilige herauthenticatie, herconfiguratie en diagnostiek zonder gevoelige gegevens.
- Geautomatiseerde tests, linting, typecontrole en CI-validatie.

## Taalondersteuning

De integratie en gebruikershandleidingen worden in het Nederlands en Engels ontwikkeld, met de native taalkeuze van Home Assistant en Engels als fallback. De daadwerkelijke integratievertalingen volgen bij de implementatie. Zie ook de [changelog](CHANGELOG.md).

## Roadmap

Zie de [geprioriteerde backlog](docs/BACKLOG.md) voor openstaande instellingen, afhankelijkheden en acceptatiecriteria.

- [x] Repositorystructuur en ontwikkelrichtlijnen vastleggen.
- [ ] NED API-client en datamodellen implementeren.
- [ ] Configuratieflow en gegevenscoördinator implementeren.
- [ ] Sensoren en voorspellingen beschikbaar maken.
- [ ] Nederlandse en Engelse integratievertalingen, diagnostiek en foutafhandeling toevoegen.
- [x] Ontwikkeltooling, pre-commit en basis-CI inrichten.
- [ ] Inhoudelijke integratietests en volledige kwaliteitsvalidatie afronden.
- [x] Marketplace-toelatingsvoorwaarden en runtime-distributiestrategie bevestigen (fase 0; daadwerkelijke catalogustoelating en installatie blijven open).
- [ ] Marketplace-compatibiliteit, metadata, branding en installatie-/updatetests realiseren.
- [ ] HACS- en Hassfest-validatie en Platinum-criteria aantoonbaar afronden.
- [ ] Na toestemming een volledige GitHub-release publiceren en een catalogus-PR bij hacs/default indienen.
- [ ] Catalogusopname na acceptatie verifiëren.

## Auteursrecht en gebruik

**Open source onder [GNU GPL versie 3 uitsluitend (GPL-3.0-only)](LICENSE).**

Gebruik, wijziging en verspreiding, ook commercieel, zijn toegestaan volgens de GPL. Bij verspreiding gelden de toepasselijke broncode-, copyleft- en vermeldingsverplichtingen. Auteursrecht en rechten van derden blijven behouden. Zie [licentietoelichting](USAGE_TERMS.md). Er is nog geen officiële projectrelease beschikbaar.

## Ondersteuning en bijdragen

Meld fouten en functievoorstellen via [GitHub Issues](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/issues). Vermeld waar relevant de Home Assistant-versie, integratieversie en stappen om het probleem te reproduceren. Verwijder persoonlijke gegevens en API-sleutels uit logbestanden.

## Referenties

- [Nationaal Energie Dashboard](https://ned.nl/)
- [Officiële NED API-documentatie, handleiding en datacatalogus](https://ned.nl/nl/api)
- [NED API](https://api.ned.nl/v1)
- [Home Assistant](https://www.home-assistant.io/)
- [Home Assistant Integration Quality Scale](https://contributors.home-assistant.io/core/quality-scale/)
- [Home Assistant Marketplace](https://contributors.home-assistant.io/marketplace/)
- [Catalogusopname](https://contributors.home-assistant.io/marketplace/guides/catalog/)

## Disclaimer

Dit is een onafhankelijk project en geen officiële integratie van het Nationaal Energie Dashboard of Home Assistant. De beschikbaarheid, actualiteit en nauwkeurigheid van energiedata zijn afhankelijk van de bron en de betreffende dataset.
