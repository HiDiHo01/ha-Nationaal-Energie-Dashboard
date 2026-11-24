# NED API-library

Zelfstandige async Python-library zonder Home Assistant-afhankelijkheid. Broncode onder src/ned_api. Verantwoordelijkheden: transport, authenticatie, parsing, catalogus, datamodellen, retries, rate limiting en exceptions.

De contractonafhankelijke packagebasis en exception-hiërarchie zijn gestart onder de beperkte vrijgave van fase 1. BL-003 blijft open. Het package bevat nu een generieke transportlaag zonder NED-specifieke client of datasetondersteuning. De distributienaam ned-api en versie 0.0.0 zijn voorlopige interne buildmetadata, geen gepubliceerde release. De naam wordt vóór publicatie gecontroleerd. De runtime-distributiestrategie is eerder synthetisch gevalideerd. Publicatie van het package vereist toestemming. Zie [integratieplan](../../docs/INTEGRATION_PLAN.md).

De actuele broncontrole en ontbrekende contractbewijzen staan in [API_REFERENCE.md](../../docs/API_REFERENCE.md).

Bouw lokaal vanuit de repository-root met `uv build --wheel --no-sources packages/ned-api`. De root `uv.lock` blijft leidend voor de gelockte ontwikkeltests; het zelfstandige package declareert een test-extra voor installatie buiten Home Assistant. Gebruik geen productiecredentials. Het lokale LICENSE-bestand is een ongewijzigde kopie van de canonieke repositorylicentie; CI controleert gelijkheid.

## Generieke transportlaag

NedTransport leent een vertrouwde certificaatvaliderende aiohttp-sessie en voert GET uit tegen één gevalideerde HTTPS-origin. Standaard ClientTimeout(total=15.0) en maximaal 2 MiB verzamelde responsebytes; dit zijn configureerbare interne ontwerpwaarden, geen NED-limieten. Absolute paden zonder URL-componenten, geen redirects, ssl=True, geen automatische decompressie; vraag identity-encoding aan en wijs andere Content-Encoding af. Geef status en bytes terug als immutable TransportResponse (body niet in repr), zonder statusmapping, JSON-parsing, credentials of applicatieretries. Cancellation blijft intact; transportfouten krijgen geschoonde exceptions zonder ruwe exceptionketen. De caller blijft eigenaar van de sessie en levert uitsluitend niet-gevoelige queryparameters. De wire- en TLS-werking, compressiecompatibiliteit en API-contract zijn niet live getest.

Runtime-dependencies: aiohttp >=3.14.5,<4 en yarl >=1.25.1,<2, beide aanwezig in de bestaande rootlock. Zie [transport.py](src/ned_api/transport.py). Geen productieaanroepen totdat de contractafhankelijke client is vrijgegeven.

De [native requirements-proef](../../scripts/check_runtime_distribution.sh) bouwt de werkelijke wheel en installeert deze naast de synthetische proef via de echte Home Assistant requirements-manager vanuit een tijdelijke offline wheelhouse. CI-bewijs van de uitbreiding is nog open. Geen packagepublicatie of integratieload.
