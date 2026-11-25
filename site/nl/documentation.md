---
lang: nl
title: Documentatie
description: Vereisten, ontwikkelstatus en ondersteuning.
permalink: /nl/documentation/
other_lang: en
other_url: /en/documentation/
---
## Installatie en vereisten

Volg de lokale alpha-testinstructies in de Nederlandse repository-README; gebruik geen HACS of publieke package-index voor de alpha.

De integratie is nog in ontwikkeling. Er is geen installeerbare release. De beoogde distributie verloopt via Home Assistant Marketplace. GPL-3.0-only is gekozen om te voldoen aan de [HACS-licentievoorwaarde](https://www.hacs.xyz/docs/publish/include/#check-license). GitHub-licentieherkenning is bevestigd; daadwerkelijke catalogustoelating blijft open. De runtime-distributiestrategie is gevalideerd met een synthetische wheel; volledige productie-installatie moet nog worden aangetoond.

De ontwikkelbranch bevat een beperkte lokale alpha (0.1.0a1): echte sleutelvalidatie, een zelfstandige UTC-kwartierparser en vijf nationale vermogenssensoren. Alleen de lokale, exact bijbehorende wheel is toegestaan voor de proefinstallatie; geen HACS-installatie of publieke release. CO₂, forecast en het geschatte hernieuwbare aandeel blijven gereserveerd totdat de contractvoorwaarden zijn vervuld. Nieuwe CI en live installatie zijn nog niet bevestigd; BL-003 en algemene fasepoorten blijven open.

Reviewherstel R39-01–08: status-first foutafhandeling, Retry-After, budget per HTTP-poging, afzonderlijke datasetbeschikbaarheid en ontvangsttijd. Gebruik de gecontroleerde lokale launcher voor de aparte testomgeving. De native lifecycle- en wheelpreflighttests moeten op de definitieve commit slagen. Geen nieuwe live probes of release.

## NED API-sleutel

Drie handmatig gerapporteerde authenticatieproeven bevestigen voor dezelfde nationale zonnequery HTTP 200 (geldige key), 401 (ontbrekend) en 403 (ongeldig). De verondersteld beperkte key krijgt toegang; rechtensemantiek blijft open. De alphaclient en Config Flow onderscheiden 401 van 403 zonder foutpayloads te loggen; de lokale eigenaarstest vereist geslaagde CI en de exacte wheel.

Maak voor toekomstig gebruik een account aan bij [NED](https://ned.nl/), open Mijn account → API en genereer een persoonlijke API-sleutel. Bewaar deze veilig. Deel nooit sleutels in issues of logs.

## Status van het API-contract

De geteste nationale P0-kwartierqueries zijn structureel gevalideerd. De NED-handleiding noemt vermogen (kW), intervalenergie (kWh), CO₂-emissies (kg) en emissiefactoren (kg CO₂/kWh). De OpenAPI-beschrijving noemt voor emissies echter ton; de onderzochte type-27-kwartierrecords ondersteunen kg, maar de formele eenheid blijft onbevestigd. Vermogen en energie zijn niet altijd exact onderling afleidbaar. Voor lokale dagtotalen is aggregatie uit volledig gevalideerde UTC-kwartieren beoogd; API-dagaggregaten blijven uitgesloten zolang de kalenderafwijkingen openstaan. De integratie is nog niet geïmplementeerd. Zie het [contractonderzoek](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/blob/main/docs/API_REFERENCE.md).

## Prioritaire sensoren

De eerste acht prioritaire nationale sensoren zijn CO₂-intensiteit, CO₂-intensiteit voorspelling, aandeel hernieuwbare elektriciteitsproductie, zon, wind op land, wind op zee, totaal elektriciteitsverbruik en totale elektriciteitsproductie. Dit is geplande functionaliteit. Het hernieuwbare aandeel wordt een herkenbaar gelabelde schatting op basis van zon, wind, bijstook van biomassa en 53% van de afvalelektriciteit (voorlopige CBS-jaarfactor 2025); overige gemengde bronnen zijn niet inbegrepen. De zes gebruikte datasets moeten eerst contractueel en gezamenlijk worden gevalideerd; BL-003 blijft open.

## Meer informatie

- [Nederlandse projectdocumentatie](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/blob/main/README.md)
- [Changelog](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/blob/main/CHANGELOG.md)
- [Meld een probleem](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/issues)
- [NED API-documentatie](https://ned.nl/nl/api)
- [Home Assistant](https://www.home-assistant.io/)
