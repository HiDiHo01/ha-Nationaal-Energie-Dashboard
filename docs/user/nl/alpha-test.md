# Lokale alpha-test 0.1.0a1

Uitsluitend een afzonderlijke Home Assistant Core-testomgeving met Core 2026.11.3 en Python 3.14.10. Geen installatie via HACS, HA OS/Supervised of een publieke package-index. Wacht op alle verplichte controles op exact de geteste commit en de afhandeling van [PR #39-review](../../PR39_REVIEW.md). Geen publieke release.

## Gecontroleerde voorbereiding en start

Gebruik een vertrouwde checkout van de beoordeelde commit en een afzonderlijke, reeds werkende Core-venv met alle UI-dependencies. Het configpad moet nieuw en absoluut zijn, met bestaande bovenliggende map. Gebruik nooit je productie-venv. Kies de volledige 40-teken-commit-SHA uit de geslaagde CI, niet een willekeurige branchversie.

```bash
HA_PYTHON="/pad/naar/test-venv/bin/python"
HA_CONFIG="/pad/naar/nieuwe-test-config"
COMMIT="<volledige-beoordeelde-commit-sha>"
bash scripts/run_local_alpha.sh prepare "$HA_PYTHON" "$HA_CONFIG" "$COMMIT"
bash scripts/run_local_alpha.sh launch "$HA_PYTHON" "$HA_CONFIG" "$COMMIT"
```

De [launcher](../../../scripts/run_local_alpha.sh) gebruikt getrackte bestanden uit de exacte Git-commit, weigert een bestaande configuratiemap bij voorbereiding, bouwt de wheel lokaal en installeert uitsluitend die wheel zonder index, cache of dependency-resolutie. De [preflight](../../../scripts/verify_alpha_wheel.sh) controleert Core/Python, SHA256, manifestpin, geïnstalleerde packagebytes en importlocatie. Bij iedere start controleert de launcher de integratiekopie en de wheel opnieuw. De lokaal opgeslagen hash is provenancecontrole binnen deze vertrouwde testomgeving, geen onafhankelijke digitale handtekening. De start gebruikt UV_NO_INDEX=1, UV_OFFLINE=1, UV_NO_CACHE=1 en --skip-pip; ontbrekende UI-dependencies moeten vooraf in de test-venv zijn geïnstalleerd uit vertrouwde bronnen. --skip-pip is uitsluitend voor deze lokale eigenaarstest; de gewone CI test de echte requirements-manager afzonderlijk. De test-UI bindt standaard aan 127.0.0.1:8124. De launcherstap start Core; voorbereiding start geen proces of NED-verzoek.

## Functionele eigenaarstest

1. Open de test-UI: Instellingen > Apparaten en diensten > Integratie toevoegen > Nationaal Energie Dashboard. Voer uitsluitend je eigen geldige API-key in via het gemaskeerde veld. Een positieve historische zonnequery valideert toegang tot die query, niet alle datasets.
2. Controleer de vijf sensoren: zon, wind land, wind zee, nationaal verbruik en nationale productie. Vergelijk native kW (aanbevolen MW), geldigheidsgrenzen, ontvangsttijd en waarden. Current kan upstream geraamde waarden bevatten. Alleen bij aanvang én ontvangst van de request afgesloten kwartieren komen in aanmerking; geen automatische promotie van eerder opgehaalde open kwartieren.
3. Controleer afzonderlijke beschikbaarheid en herstel. Een mislukte dataset blijft unavailable; andere geslaagde datasets blijven bruikbaar. Geen nulvulling. Alle datasets mislukt, HTTP 401 of 429 blokkeert de batch; 403 blijft ambigu. Intervalgrens 30 minuten blijft voorlopig; cachecallback doet geen HTTP. Per refresh maximaal vijf logische dagqueries, of tien bij UTC-overlap; aiohttp kan intern een GET herhalen. Middleware telt iedere poging, inclusief fouten en interne retries. Proceslokaal budget 120 pogingen/300 seconden. HTTP 429 blokkeert nieuwe aanvragen minstens 300 seconden en respecteert een langere geldige Retry-After; boven 24 uur blijft de limiter voor dit proces geblokkeerd. Herstart niet om een serverbeperking te omzeilen. Geen negatieve of belastingproeven.
4. Test reload, herconfiguratie en unload met normale geldige credentials; stop bij ongewoon gedrag. Deel uitsluitend geschoonde meldingen, statuscodes en waarnemingen.

## Stoppen en terugdraaien

Verwijder de integratie via de test-UI, stop de afzonderlijke Core-procesinstantie en controleer dat deze niet meer actief is. Bewaar desgewenst een veilige backup van de testconfiguratie; deze kan credentials bevatten. Verwijder daarna uitsluitend de eigen testconfiguratie en aparte test-venv indien niet meer nodig. De launcher verwijdert geen bestaande gebruikersconfiguratie. Start geen productie-installatie vanuit deze alpha.

CO₂, forecast, geschat hernieuwbaar aandeel, dagaggregatie en revisieverwerking blijven buiten scope. Volledige autorisatiesemantiek, daadwerkelijke publicatielatency, upstream quota-scope en formele NED Retry-After-semantiek blijven onbevestigd. Een eigenaarstest is geen volledige faseacceptatie of productierelease.
