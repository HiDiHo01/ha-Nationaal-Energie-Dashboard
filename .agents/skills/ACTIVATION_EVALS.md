# Skillactivatie — evaluaties

Doel: verifieer dat een agent de relevante skills zonder expliciete skillnaam selecteert, de volledige instructies leest en de juiste procedure toepast. De testmethodiek volgt [Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills).

## Scenario's

Gebruik de prompts ongewijzigd, in een nieuwe sessie per scenario. De verwachte skills zijn minimaal vereist voor de beschreven taak; aanvullende relevante skills zijn toegestaan. Een daadwerkelijk geblokkeerde implementatie mag niet worden geforceerd.

| ID | Prompt | Verwachte skill(s) | Bewijs |
| --- | --- | --- | --- |
| NL01 | Maak een configuratieflow met herauthenticatie. | ha-integration, ha-quality-verification | Native flow, behoud identiteit, passende tests of expliciete prerequisites. |
| EN01 | Implement a config flow with reauthentication. | ha-integration, ha-quality-verification | Same contract and lifecycle checks. |
| NL02 | Controleer hoe de NED API authenticatie en paginering afhandelt. | ned-api-contract | Primaire bronnen, bevestigde feiten apart van aannames. |
| EN02 | Verify NED API authentication and pagination. | ned-api-contract | Source-backed contract, no unauthorized live requests. |
| NL03 | Controleer de berekening van CO₂-intensiteit tijdens de overgang naar wintertijd. | energy-data-semantics, ha-quality-verification | Energiegewogen berekening, DST, emissie-eenheid kg/ton als hypothese (SEM-002: 192 kg-overeenkomsten), SEM-001: 32 grotere afwijkingen, geen automatische correctie of productietolerantie, geen nulvulling, tests. |
| EN03 | Review CO2 intensity calculations across the autumn clock change. | energy-data-semantics, ha-quality-verification | Units, kg/ton hypothesis not a guarantee (SEM-002: 192 kg matches), SEM-001: 32 larger discrepancies, no automatic correction or production tolerance, interval coverage, no zero filling and DST tests. |
| NL04 | Onderzoek waarom onze CI faalt en herstel de workflow. | ci-workflow-maintenance | Relevante logs, oorzaak, veilige fix en verificatie; toets bestaande Bash-beleidslogica met gesimuleerde gh en echte jq, zonder echte merge; onderscheid Pages-build, deploy en publieke HTTPS-verificatie. |
| EN04 | Diagnose and repair the failing GitHub Actions workflow. | ci-workflow-maintenance | Same checks, no lowered quality gates; test existing Bash policy with mocked gh and real jq, no actual merge; distinguish Pages build, deployment and public HTTPS verification. |
| NL05 | Controleer alle Platinum-criteria. | ha-quality-verification | Bewijsmatrix, geen onbewezen status done. |
| EN05 | Audit integration quality against Platinum. | ha-quality-verification | Evidence and missing prerequisites. |
| NL06 | Bereid de integratie voor op opname in de Marketplace. | marketplace-readiness, ha-quality-verification | Validatie, OSI-licentiecontrole, GPL-3.0-only en GitHub-herkenning, huidige gebruiksrechten en onderscheid custom repository/catalogus, geen ongeautoriseerde publicatie of versoepeling. |
| EN06 | Prepare the integration for Marketplace admission. | marketplace-readiness, ha-quality-verification | Admission checks, OSI license check, GPL-3.0-only and GitHub detection, current usage rights and distinction between custom repository and catalog, no unauthorized publication or weakened checks. |
| NL07 | Actualiseer de ontwikkelrichtlijnen met bewezen nieuwe Home Assistant-kennis. | project-knowledge-maintenance | Bronnen, datum, consistente instructies en autonome documentatie-impactanalyse. |
| EN07 | Update the repository guidance with verified new Home Assistant knowledge. | project-knowledge-maintenance | Verified references, consistent guidance and autonomous documentation impact review. |
| NL09 | Herstel de falende Ruff-format required check en voorkom herhaling. | ha-quality-verification, ci-workflow-maintenance | Exacte formatterdiff (PR #16 Query en PR #21 assertEqual), gelockte Ruff-versie, definitieve formatcheck inclusief testbestanden, format en lint apart, controle van nieuwe commit en herhaalde CI; geen testlogica aanpassen; eerlijke lokale beperkingen. |
| EN09 | Fix the failing Ruff format required check and prevent recurrence. | ha-quality-verification, ci-workflow-maintenance | Same locked formatter, exact diff (PR #16 Query and PR #21 assertEqual), final format check including tests, separate lint/format checks, unchanged assertions and new-commit CI evidence; disclose local limitations. |
| NL10 | Beoordeel een NED-dagrecord met correcte duur maar verschoven kalendergrenzen en een wintertijddag van 24 uur. | energy-data-semantics, ned-api-contract | Begin, einde en duur onafhankelijk toetsen; upstream-dagaggregatie uitsluiten, granularity 4/timezone 0, afzonderlijke lokale middernachten naar UTC, overlappende UTC-dagen en 92/96/100 kwartieren, meetsemantiek en volledige dekking; geen stille correctie of ongeautoriseerde live-aanvraag. |
| EN10 | Assess a NED daily record with correct duration but shifted calendar boundaries and a 24-hour autumn DST day. | energy-data-semantics, ned-api-contract | Independently validate start, end and duration; reject upstream daily aggregation, use granularity 4/timezone 0, convert local midnights separately to UTC, overlapping UTC days and 92/96/100 quarters, validate semantics and full coverage; no silent correction or unauthorized live request. |
| NL11 | Valideer de zelfstandige API-library als Home Assistant-runtime dependency zonder publicatie. | marketplace-readiness, ha-quality-verification | Tijdelijke wheel, exacte Core/Python-baseline, native requirements-manager, geïsoleerde import en dependencycheck; geen publicatie of claim van volledige installatie. |
| EN11 | Validate the standalone API library as a Home Assistant runtime dependency without publishing it. | marketplace-readiness, ha-quality-verification | Temporary wheel, exact Core/Python baseline, native requirements manager, isolated import and dependency check; no publication or full installation claim. |
| NEG01 | Vertaal 'good morning' naar Nederlands. | Geen projectspecifieke skill nodig | Geen onnodige activatie. |
| NL08 | Voeg een gebruikersgerichte wijziging toe aan de integratie en actualiseer de documentatie. | ha-integration, ha-quality-verification, project-knowledge-maintenance | Gelijke NL/EN-keys, placeholders, beide gebruikersdocumentatieversies en validator of expliciete implementatieblokkade. |
| EN08 | Add a user-facing integration change and update its documentation. | ha-integration, ha-quality-verification, project-knowledge-maintenance | Matching NL/EN keys and placeholders, both user-documentation versions and validator evidence or explicit implementation blocker. |

## Uitvoering en beoordeling

1. Open een schone, geïsoleerde checkout van de te evalueren commit in een agentomgeving met native skill-discovery. Controleer dat de zeven repositoryskills beschikbaar zijn. Gebruik geen productiecredentials en publiceer niets.
2. Start per scenario een nieuwe sessie zonder expliciete skillvermelding of vooraf geladen volledige SKILL.md. Registreer agentversie, model, commit en prompt-ID.
3. Controleer in de beschikbare trace of de agent de verwachte SKILL.md-bestanden daadwerkelijk heeft geladen. Een vermelding in de eindtekst alleen is geen bewijs. Als de omgeving geen native discovery ondersteunt, evalueer de directe bestandsleesprocedure afzonderlijk.
4. Beoordeel selectie, onnodige activatie, proceduretrouw, resultaatkwaliteit en respect voor de bestaande bevoegdheden. Registreer ontbrekende prerequisites als geblokkeerd, niet als geslaagd. Voer geen betaalde externe evaluaties zonder toestemming uit.
5. Herhaal relevante scenario's na wijzigingen in skillbeschrijvingen, metadata of instructies. Herstel aangetoonde tekortkomingen en bewaar de resultaten met trace-referenties. Een statische metadatacontrole is geen gedragsevaluatie.

## Uitvoerbare runner

Gebruik een Linux/Bash-omgeving met git, tar, awk en een geïnstalleerde, geauthenticeerde Codex CLI. Gebruik een afzonderlijke evaluatieomgeving zonder productiecredentials, niet-vertrouwde hooks, extra schrijfgebieden of verbonden tools met externe schrijfrechten. Controleer vooraf de gecommitteerde inhoud op secrets. Het gebruik van de CLI kan modelverbruik veroorzaken; voer alleen geautoriseerde evaluaties uit.

Vanuit een checkout van de te beoordelen commit:

```bash
output_dir=$(mktemp -d)
bash .agents/skills/run-native-eval.sh NL01 "$output_dir"
```

De runner selecteert de originele prompt op scenario-ID, exporteert alleen gecommitteerde bestanden naar een tijdelijke Git-repository zonder remote, voert een nieuwe Codex-sessie met JSONL-uitvoer en workspace-write sandbox zonder shellnetwerktoegang uit en bewaart metadata, stderr, trace en werkboomdiff buiten de bronrepository. De tijdelijke checkout wordt verwijderd. Niet-gecommitteerde bronwijzigingen worden niet geëvalueerd; genegeerde of binaire output vereist zo nodig een afzonderlijke inspectie in een geschikte evaluatieomgeving. Controleer de CLI-versie en het gebruikte model (uit de trace of sessie-informatie) bij de beoordeling. De sandbox is geen vervanging voor een afzonderlijke veilige omgeving.

Beoordeel de opgeslagen trace aan de hand van de scenariotabel: verwachte skill-read/invocation aantoonbaar, ongewenste activatie, proceduretrouw, uitkomst en beleidsnaleving. Noteer per controle pass, fail, blocked of unverified, met concrete traceverwijzingen. Gebruik voor de negatieve controle bewijs dat de volledige relevante trace beschikbaar is. Bewaar de ruwe traces privé; commit alleen geschoonde resultaten, nooit secrets of ruwe traces. Een exitcode 0 betekent uitsluitend dat de CLI-aanroep is voltooid, niet dat de evaluatie is geslaagd. Exitcode 3 van de preflight betekent ontbrekende CLI.

## Status

De scenario's en runner zijn voorbereid; native activatie en proceduretrouw zijn nog niet empirisch geëvalueerd. Op 24 november 2026 is de runner syntactisch gecontroleerd met bash -n en getest met een gesimuleerde CLI (succes, foutcode, onbekend scenario, behoud van nieuwe en gecommitteerde testoutput); de ontbrekende echte CLI is correct gemeld. Dit zijn uitsluitend runnercontroles, geen native gedragsevaluaties. Er is geen Codex-sessietrace beschikbaar vanuit de huidige GitHub-connectoromgeving. Rapporteer native en directe activatie afzonderlijk.

### Eigenaarsbesluit BL-012 — 24 november 2026

De afzonderlijke taak voor installatie en authenticatie van een Codex CLI-evaluatieomgeving vervalt. Vraag de eigenaar niet opnieuw om deze omgeving in te richten. Behoud de runner en alle 23 scenario's voor een eventueel reeds beschikbare, geschikte en geautoriseerde native omgeving. BL-013 blijft niet uitgevoerd en geblokkeerd zolang native tracebewijs ontbreekt; directe selectie, statische validatie en reguliere CI zijn geen vervangend native bewijs. De bestaande kwaliteitsacceptatiecriteria zijn niet gewijzigd. Geen betaalde evaluaties of nieuwe credentials.
