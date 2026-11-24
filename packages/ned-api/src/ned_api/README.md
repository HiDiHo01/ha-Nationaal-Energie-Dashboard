# API-client broncode

De contractonafhankelijke exception-hiërarchie staat in [exceptions.py](exceptions.py); de publieke exports staan in [__init__.py](__init__.py). py.typed markeert de getypeerde library. De generieke transportlaag staat in [transport.py](transport.py); contractafhankelijke modules blijven geblokkeerd. Injecteer de HTTP-sessie en sluit een geleende sessie niet. Voeg geen lege Python-modules toe.

De publieke NedTransport en TransportResponse blijven contractonafhankelijk. Zie de [packagebeschrijving](../../README.md) voor grenzen en eigenaarschap.
