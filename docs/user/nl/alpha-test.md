# Lokale alpha-test 0.1.0a1

Deze proef is uitsluitend bedoeld voor een afzonderlijke, reeds werkende Home Assistant Core-testomgeving met Core 2026.11.3 en Python 3.14.10. Geen installatie op de productieomgeving, via HACS of via een publieke index. Wacht met een eigenaarstest totdat alle verplichte CI-controles op exact de te testen commit zijn geslaagd. Er is geen publieke release of PyPI-publicatie.

## Voorbereiding en installatie

Controleer de herkomst van de checkout en de exacte commit in PR #39; voer onderstaande opdrachten uit vanaf de repositoryroot op de testmachine. Stel de twee paden in op je afzonderlijke testomgeving (niet de productieomgeving).

```bash
HA_PYTHON="/pad/naar/test-venv/bin/python"
HA_CONFIG="/pad/naar/test-config"
"$HA_PYTHON" -c 'import sys; from importlib.metadata import version; assert sys.version_info[:3] == (3, 14, 10); assert version("homeassistant") == "2026.11.3"'
uv build --wheel --no-sources --out-dir wheelhouse packages/ned-api
sha256sum wheelhouse/ned_api-0.1.0a1-py3-none-any.whl
uv pip install --python "$HA_PYTHON" --no-index --no-deps --reinstall wheelhouse/ned_api-0.1.0a1-py3-none-any.whl
uv pip check --python "$HA_PYTHON"
"$HA_PYTHON" -c 'from importlib.metadata import version; assert version("ned-api") == "0.1.0a1"; import ned_api; print(ned_api.__file__)'
mkdir -p "$HA_CONFIG/custom_components"
cp -R custom_components/nationaal_energie_dashboard "$HA_CONFIG/custom_components/"
```

Gebruik een schone testconfiguratie zonder oudere kopie van de integratie. Bouw de wheel zelf uit dezelfde commit; vergelijk de hash met je eigen buildadministratie en installeer geen gelijknamig package van een publieke index. De gelockte ontwikkelomgeving en de [native wheelproef](../../../scripts/check_runtime_distribution.sh) zijn de referentie voor dependencycompatibiliteit. Stop bij ontbrekende of conflicterende dependencies. De alpha veronderstelt dat Home Assistant en zijn overige vereisten al zijn geïnstalleerd; de installatie van HA OS/Supervised en HACS is nog niet gevalideerd. Herstart de testinstantie met `UV_NO_INDEX=1 UV_OFFLINE=1` om externe package-resolutie tijdens deze proef te voorkomen.

## Functionele eigenaarstest

1. Open Instellingen > Apparaten en diensten > Integratie toevoegen > Nationaal Energie Dashboard. Voer uitsluitend je eigen geldige API-key in via het gemaskeerde veld; deel de sleutel niet. Eén positieve historische zonnequery valideert toegang.
2. Controleer de vijf sensoren: zon, wind land, wind zee, nationaal verbruik en nationale productie. Vergelijk eenheden (native kW, aanbevolen MW), geldigheidsgrenzen en waarden met NED. Current kan upstream geraamde waarden bevatten.
3. Controleer dat ontbrekende, ongeldige of verouderde waarden unavailable worden en niet nul. Er worden per refresh maximaal vijf aanvragen gedaan, of tien bij UTC-dagoverlap. Vijf minuten tussen reguliere updates; geen applicatieretries. Stop bij ongewoon gedrag of HTTP 429, voer geen negatieve of belastingproeven uit.
4. Test reload en unload in de testomgeving en controleer dat polling stopt. Deel uitsluitend geschoonde foutmeldingen, statuscodes en waarnemingen; geen credentials, ruwe responsebody of configuratieopslag.

CO₂, forecast en geschat hernieuwbaar aandeel worden niet geregistreerd in deze alpha. Dagaggregatie, revisieverwerking, volledige autorisatiesemantiek en universele rate-limitgaranties zijn niet bevestigd. De 30-minuten-stalegrens en het proceslokale budget zijn conservatieve ontwerpkeuzes. Een geslaagde eigenaarstest is geen volledige faseacceptatie of productierelease.
