# NED API-library

Zelfstandige async Python-library zonder Home Assistant-afhankelijkheid. Broncode onder src/ned_api. Verantwoordelijkheden: transport, authenticatie, parsing, catalogus, datamodellen, retries, rate limiting en exceptions.

De contractonafhankelijke packagebasis en exception-hiërarchie zijn gestart onder de beperkte vrijgave van fase 1. BL-003 blijft open. Dit package heeft nog geen HTTP-client of datasetondersteuning. De distributienaam ned-api en versie 0.0.0 zijn voorlopige interne buildmetadata, geen gepubliceerde release. De naam wordt vóór publicatie gecontroleerd. De runtime-distributiestrategie is eerder synthetisch gevalideerd. Publicatie van het package vereist toestemming. Zie [integratieplan](../../docs/INTEGRATION_PLAN.md).

De actuele broncontrole en ontbrekende contractbewijzen staan in [API_REFERENCE.md](../../docs/API_REFERENCE.md).

Bouw lokaal vanuit de repository-root met `uv build --wheel --no-sources packages/ned-api`. De root `uv.lock` blijft leidend voor de gelockte ontwikkeltests; het zelfstandige package declareert een test-extra voor installatie buiten Home Assistant. Gebruik geen productiecredentials. Het lokale LICENSE-bestand is een ongewijzigde kopie van de canonieke repositorylicentie; CI controleert gelijkheid.
