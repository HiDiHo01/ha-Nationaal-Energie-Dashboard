# Changelog / Wijzigingen

## Unreleased

### Nederlands

- Acht prioritaire nationale sensoren vastgelegd; CO₂-forecast volgt fase 4 en het hernieuwbare elektriciteitsaandeel vereist aanvullend bronmixbewijs. Geen sensorimplementatie of wijziging van de fasepoorten.

- Contractonafhankelijke asynchrone HTTPS-transportlaag met sessie-injectie, responslimiet, time-outs en geschoonde exceptions; 38 nieuwe synthetische tests. NED-specifieke verwerking blijft geblokkeerd door BL-003.

- Beperkte fase 1 gestart op eigenaarsbesluit: zelfstandige packagebasis, getypeerde exception-hiërarchie en eerste synthetische tests; BL-003 blijft open. Wheel- en kwaliteitsvalidatie op de productie-baseline volgt via CI.

- Openbare documentatie in beide talen afgestemd op de waargenomen kwartiercontracten, de onbevestigde emissie-eenheid en de uitsluiting van upstream-dagaggregaten.

- Gerichte dagaggregatieprobe voor TZ-002/TZ-003 met twee vaste aanvragen, intervalduur en afzonderlijke grensafwijkingen; beide afwijkingen live bevestigd, oorzaakanalyse blijft open.

- Nationale P0-datasets en paginering live gevalideerd voor de geteste queries; NL-kwartierdekking voor historische zon bevestigd, afwijkende recordtijdzone en twee dagaggregatie-afwijkingen vastgelegd. Verdere contractvalidatie blijft open.

- Tweetalige projectsite gemigreerd naar Jekyll met gedeelde layouts, gelockte gems en gecontroleerde Pages-deployment.

- Eerste geauthenticeerde NED-contractobservaties geslaagd via de beveiligde opt-in workflow; OpenAPI-veldtypeverschillen vastgelegd. Volledige contractvalidatie blijft open.

- Repositoryfundament, technische ontwikkelrichtlijnen en autonome documentatie- en skillonderhoudsregels.
- Gelockte Python-ontwikkelomgeving, pre-commit, VS Code, Baseline CI en dependency-audits.
- Branchbescherming en gecontroleerde Dependabot-auto-merge; echte botmergevalidatie staat nog open.
- Nederlands en Engels als verplichte gebruikerstalen, beide README-versies en automatische documentatie- en vertaalcontroles.
- Marketplace als beoogd distributiekanaal; GPL-3.0-only gekozen om aan de OSI-licentievoorwaarde te voldoen. GitHub-herkenning bevestigd; catalogustoelating blijft open.
- Synthetische runtime-wheel via native Home Assistant requirements-manager gevalideerd; initiële ADR's vastgelegd. Volledige installatie blijft open.
- Beperkte gebruikstoestemming vervangen door GPL-3.0-only; country NL toegevoegd aan hacs.json.
- Nog geen installeerbare integratie, daadwerkelijke integratievertalingen of publieke release.

### English

- Eight priority national sensors specified; the CO₂ forecast follows phase 4 and renewable electricity share requires further source-mix evidence. No sensor implementation or change to the phase gates.

- Contract-independent asynchronous HTTPS transport with session injection, response size limit, timeouts and sanitized exceptions; 38 new synthetic tests. NED-specific processing remains blocked by BL-003.

- Partial phase 1 started by owner decision: independent package foundation, typed exception hierarchy and initial synthetic tests; BL-003 remains open. Wheel and quality validation on the production baseline is pending CI.

- Public documentation in both languages aligned with observed quarter-hour contracts, the unconfirmed emission unit and exclusion of upstream daily aggregates.

- Focused daily aggregation probe for TZ-002/TZ-003 with two fixed requests, interval duration and separate boundary offsets; both deviations confirmed live, root cause remains unresolved.

- National P0 datasets and pagination validated live for the tested queries; Dutch quarter-hour coverage for historical solar data confirmed, differing record timezone and two daily aggregation discrepancies documented. Further contract validation remains pending.

- Bilingual project site migrated to Jekyll with shared layouts, locked gems and guarded Pages deployment.

- Initial authenticated NED contract observations passed through the secured opt-in workflow; OpenAPI field type differences documented. Full contract validation remains open.

- Repository foundation, technical development guidelines and autonomous documentation and skill maintenance rules.
- Locked Python development environment, pre-commit, VS Code, baseline CI and dependency audits.
- Branch protection and guarded Dependabot auto-merge; real bot merge validation remains open.
- Dutch and English as required user languages, both README versions and automated documentation and translation checks.
- Marketplace as the intended distribution channel; GPL-3.0-only chosen to meet the OSI license requirement. GitHub detection confirmed; catalog admission remains pending.
- Synthetic runtime wheel validated through the native Home Assistant requirements manager; initial ADRs recorded. Full installation remains pending.
- Limited usage permission replaced by GPL-3.0-only; country NL added to hacs.json.
- No installable integration, actual integration translations or public release yet.
