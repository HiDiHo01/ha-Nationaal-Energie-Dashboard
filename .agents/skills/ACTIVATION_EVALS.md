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
| NL03 | Controleer de berekening van CO₂-intensiteit tijdens de overgang naar wintertijd. | energy-data-semantics, ha-quality-verification | Energiegewogen berekening, DST en tests. |
| EN03 | Review CO2 intensity calculations across the autumn clock change. | energy-data-semantics, ha-quality-verification | Units, interval coverage and DST tests. |
| NL04 | Onderzoek waarom onze CI faalt en herstel de workflow. | ci-workflow-maintenance | Relevante logs, oorzaak, veilige fix en verificatie. |
| EN04 | Diagnose and repair the failing GitHub Actions workflow. | ci-workflow-maintenance | Same checks, no lowered quality gates. |
| NL05 | Controleer alle Platinum-criteria. | ha-quality-verification | Bewijsmatrix, geen onbewezen status done. |
| EN05 | Audit integration quality against Platinum. | ha-quality-verification | Evidence and missing prerequisites. |
| NL06 | Bereid de integratie voor op opname in de Marketplace. | marketplace-readiness, ha-quality-verification | Validatie, gebruiksrechten, geen ongeautoriseerde publicatie. |
| EN06 | Prepare the integration for Marketplace admission. | marketplace-readiness, ha-quality-verification | Admission checks and publication boundary. |
| NL07 | Actualiseer de ontwikkelrichtlijnen met bewezen nieuwe Home Assistant-kennis. | project-knowledge-maintenance | Bronnen, datum en consistente instructies. |
| EN07 | Update the repository guidance with verified new Home Assistant knowledge. | project-knowledge-maintenance | Verified references and consistent guidance. |
| NEG01 | Vertaal 'good morning' naar Nederlands. | Geen projectspecifieke skill nodig | Geen onnodige activatie. |

## Uitvoering en beoordeling

1. Open een schone, geïsoleerde checkout van de te evalueren commit in een agentomgeving met native skill-discovery. Controleer dat de zeven repositoryskills beschikbaar zijn. Gebruik geen productiecredentials en publiceer niets.
2. Start per scenario een nieuwe sessie zonder expliciete skillvermelding of vooraf geladen volledige SKILL.md. Registreer agentversie, model, commit en prompt-ID.
3. Controleer in de beschikbare trace of de agent de verwachte SKILL.md-bestanden daadwerkelijk heeft geladen. Een vermelding in de eindtekst alleen is geen bewijs. Als de omgeving geen native discovery ondersteunt, evalueer de directe bestandsleesprocedure afzonderlijk.
4. Beoordeel selectie, onnodige activatie, proceduretrouw, resultaatkwaliteit en respect voor de bestaande bevoegdheden. Registreer ontbrekende prerequisites als geblokkeerd, niet als geslaagd. Voer geen betaalde externe evaluaties zonder toestemming uit.
5. Herhaal relevante scenario's na wijzigingen in skillbeschrijvingen, metadata of instructies. Herstel aangetoonde tekortkomingen en bewaar de resultaten met trace-referenties. Een statische metadatacontrole is geen gedragsevaluatie.

## Status

De scenario's zijn voorbereid; native activatie en proceduretrouw zijn nog niet empirisch geëvalueerd. Er is geen Codex-sessietrace beschikbaar vanuit de huidige GitHub-connectoromgeving. Rapporteer native en directe activatie afzonderlijk.
