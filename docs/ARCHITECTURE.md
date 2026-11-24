# Architectuur

De technische baseline staat in [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md), hoofdstukken 4–11.

- Home Assistant-entiteiten lezen getypeerde coordinator-snapshots.
- Current en forecast hebben afzonderlijke coordinators; historie is on-demand.
- De zelfstandige NED-library beheert HTTP, authenticatie, parsing en requestbudget.
- De runtime gebruikt een geïnjecteerde aiohttp-sessie.
- De Marketplace installeert één integratiemap; Home Assistant installeert de zelfstandige library als exact gepinde wheel via manifest requirements (ADR-003).

Status: ontwerp, nog niet geïmplementeerd.

## Architectuurbesluiten (ADR's)

Deze registratie legt besluit, onderbouwing en bewijs vast. Het integratieplan blijft de canonieke bron voor uitvoeringsdetails en fasepoorten. Status geaccepteerd betekent niet dat productiefunctionaliteit is geïmplementeerd. Vervang een besluit alleen met een traceerbaar opvolgend ADR en de vereiste bevoegdheid.

### ADR-001 — Nederlandse kalenderaggregatie uit UTC-kwartierdata

- Datum: 24 november 2026.
- Status: geaccepteerd door eigenaar; productie-implementatie en meetsemantiek open.
- Context: TZ-002 mist één uur kalenderdekking op de wintertijddag; TZ-003 is 23 uur verschoven.
- Besluit: granularity 4, granularitytimezone 0, timezone-aware UTC-opslag; Nederlandse kalendergrenzen via Europe/Amsterdam en lokale aggregatie uit volledige kwartierdekking.
- Motivatie: correcte duur of tijdzone-ID bewijst geen correcte kalendergrenzen. De geteste kwartierdata bieden een betrouwbaarder uitgangspunt.
- Gevolgen: query overlappende UTC-dagen begrensd; valideer revisies, dekking, classificatie en meetsemantiek. Geen upstream-dagaggregaten zolang TZ-002/TZ-003 openstaan.
- Bewijs: [PR #17](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/pull/17), [dagprobe](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45478763623/job/138745945524), [integratieplan §15](INTEGRATION_PLAN.md#15-tijdzonebeheer-en-historie).

### ADR-002 — GPL-3.0-only voor catalogustoelating

- Datum: 24 november 2026.
- Status: geaccepteerd op expliciete eigenaarsopdracht; licentievoorwaarde bevestigd, catalogusopname open.
- Context: de eerdere niet-commerciële gebruikstoestemming voldoet niet aan de reguliere OSI-licentiecontrole van HACS.
- Besluit: GPL-3.0-only voor projecteigen materiaal, zonder extra restricties.
- Motivatie: OSI-goedgekeurd, herkenbaar door GitHub, sterk copyleft.
- Gevolgen: commerciële toepassing, wijziging en distributie onder GPL toegestaan; rechten van derden blijven behouden. Officiële projectpublicatie blijft afzonderlijk geautoriseerd.
- Bewijs: [LICENSE](../LICENSE), [PR #18](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/pull/18), GitHub license.key=gpl-3.0 op main 52d19849fbae09b619a6f0eb06d3943d3b4e24df, [integratieplan §26.3](INTEGRATION_PLAN.md#263-auteursrecht-en-distributiebesluit).

### ADR-003 — Zelfstandige wheel via native requirements

- Datum: 24 november 2026.
- Status: geaccepteerd binnen de bestaande zelfstandige API-architectuur; synthetische fase-0-proef geslaagd; productiereleasevalidatie open.
- Context: HACS distribueert de integratiemap; eindgebruikers hebben geen ontwikkelaarscheckout. De zelfstandige API-library moet zonder Home Assistant-afhankelijkheid testbaar blijven.
- Besluit: bouw de library afzonderlijk en gebruik een exact gepinde distributie in manifest requirements; Home Assistant verzorgt installatie. PyPI-publicatie uitsluitend na afzonderlijke toestemming.
- Motivatie: native installer, onafhankelijk versiebeheer en geen runtime Git- of PYTHONPATH-workaround.
- Gevolgen: controleer distributienaam, buildmetadata, dependencycompatibiliteit en echte wheel/installatie bij fase 1 en 7. De tijdelijke offline wheelhouse-proef is geen volledige HACS-installatie of publieke PyPI-proef.
- Bewijs: [PR #19](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/pull/19), [geslaagde CI-job](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45482964831/job/138760699296), Core 2026.11.3/Python 3.14.10 en 164 gecontroleerde packages; [integratieplan §26.1](INTEGRATION_PLAN.md#261-beperkingen-en-ontwerpbeslissingen).

- Aanvullende fase-1-validatie: de [native runtimeproef](../scripts/check_runtime_distribution.sh) omvat nu ook de daadwerkelijke API-wheel naast de synthetische wheel. Gelockte CI-uitvoering van deze uitbreiding nog te bevestigen; volledige integratie- en releasevalidatie blijft open.
