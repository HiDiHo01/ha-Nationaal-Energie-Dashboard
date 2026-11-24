# Backlog — Nationaal Energie Dashboard

Laatste inventarisatie: 24 november 2026.

Deze backlog concretiseert de openstaande instellingen en vervolgstappen uit de ontwikkelinventarisatie. Het [integratieplan](INTEGRATION_PLAN.md) blijft de bron voor scope, fasen en acceptatiepoorten; [AGENTS.md](../AGENTS.md) en [AI_POLICY.md](../AI_POLICY.md) blijven leidend. De backlog is geen toestemming om afhankelijkheden of beleidsgrenzen te omzeilen.

## Prioritering en beheer

- Hoog: noodzakelijke fundamenten of expliciete gebruikersvereisten. Normaal: ondersteunende ontwikkelkwaliteit. Later: afhankelijk van verdere implementatie.
- Werk zelfstandig aan de eerstvolgende uitvoerbare taak binnen de geldende opdracht. Blokkades verhinderen geen onafhankelijke werkzaamheden.
- Houd ID's stabiel. Actualiseer status, afhankelijkheden en acceptatiebewijs bij relevante opleveringen; sluit een item pas nadat de acceptatiecriteria aantoonbaar zijn behaald. Synchroniseer het integratieplan en de README-roadmap zonder dubbel werk te creëren.
- Gebruikersactie vereist een beschikbare bevoegdheid, veilige toegang of expliciete toestemming; een backlogitem alleen verleent die niet. Wacht met afhankelijke handelingen totdat de benodigde voorwaarde is vervuld.
- Gebruik de relevante [repositoryskills](../.agents/skills/README.md), waaronder project-knowledge-maintenance. Rapporteer echte testresultaten en eventuele blokkades.

## Openstaande instellingen en vervolgstappen

| ID | Prioriteit | Fase | Status | Taak | Acceptatiecriteria | Afhankelijkheid |
| --- | --- | --- | --- | --- | --- | --- |
| BL-001 | Hoog | 0 | Gereed | uv.lock afronden | Beoordeel de kandidaat uit Baseline CI, controleer herkomst en dependencies, commit uv.lock en laat uv lock --check, uv sync --locked, uv pip check en pip-audit op de exacte Core/Python-baseline slagen. | Gecontroleerde lockfile; zie bewijs hieronder. |
| BL-002 | Hoog | 0 | Open | Pre-commit en ontwikkelomgeving | Voeg .pre-commit-config.yaml toe met reproduceerbare hooks die de centrale toolconfiguratie gebruiken; documenteer installatie en valideer toepasselijke hooks. | BL-001 |
| BL-003 | Hoog | 0 | Open | NED API-contract verifiëren | Verifieer OpenAPI, endpoints, authenticatie, datasets, combinaties, eenheden, paginering, tijdzones, foutcodes en limieten met primaire bronnen en waar nodig geautoriseerde live tests. Leg bewijs en open vragen vast vóór afhankelijke implementatie. | BL-004 voor geauthenticeerde verificatie. |
| BL-004 | Hoog | 0 | Gebruikersactie | Veilige NED API-authenticatie | Regel een bevoegde test-API-key via een veilige secret-injectiemethode; voor GitHub Actions uitsluitend via een afgeschermde opt-in contractworkflow. Geen keys in chat, broncode, logs of fixtures. | Eigenaar; workflow en secretnaam eerst vaststellen. |
| BL-005 | Hoog | 0 | Open | Marketplace-toelatingsvoorwaarden | Bevestig actuele toelatings- en licentievoorwaarden tegen USAGE_TERMS.md. Vraag de eigenaar bij een noodzakelijke wijziging van rechten; geen impliciete licentieverlening. | Geen; externe voorwaarden verifiëren. |
| BL-006 | Hoog | 0 | Open | Runtime-distributiestrategie | Valideer een reproduceerbare Marketplace-compatibele installatiemethode voor de zelfstandige API-library op een schone ondersteunde HA-omgeving, zonder ongeautoriseerde publicatie. | BL-005; representatief package-/installatieprototype. |
| BL-007 | Hoog | 0 | Open | Autonoom documentatiebeheer | Leg verplicht zelfstandig onderhoud vast in AGENTS.md, relevante skills en Definition of Done. Houd README, changelog, roadmap, backlog, technische referenties en gebruikersdocumentatie synchroon met geverifieerde code, tests en CI. Automatiseer zinvolle documentatiecontroles en controleer links. | Geen; eerdere gebruikersopdracht nog niet volledig opgeslagen. |
| BL-008 | Hoog | 0–7 | Open | NL/EN-taalbeleid | Leg Nederlands en Engels als gelijkwaardige verplichte gebruikerstalen vast, inclusief gebruikersdocumentatie. Volg native HA-taalkeuze; Engels als fallback na verificatie. Controleer de custom-integration-vertaalstructuur, identieke vereiste keys en placeholders, en automatiseer vertaalvalidatie zodra vertaalbestanden bestaan. Geen lege placeholdervertalingen. | Beleid in fase 0; vertalingen per functionele wijziging. |
| BL-009 | Normaal | 0 | Open | Architectuurbesluiten (ADR's) | Leg concrete belangrijke beslissingen vast met context, besluit, motivatie, gevolgen, status en bewijs. Gebruik links naar het integratieplan; voorkom dubbele architectuurbronnen. | Besluiten o.a. BL-005 en BL-006. |
| BL-010 | Normaal | 0 | Open | VS Code-ontwikkelomgeving | Configureer nuttige repositorygebonden editorinstellingen en aanbevolen extensies voor Python, Ruff, typing en tests; geen machinegebonden paden of secrets. | BL-001 en BL-002 |
| BL-011 | Normaal | 0 | Gereed | Branch protection | Bereid het branch- en required-checkbeleid voor. Laat de eigenaar expliciet toestemming geven voordat repository-instellingen worden gewijzigd. Activeer alleen aantoonbaar werkende toepasselijke checks; experimentele Python-next-job blijft niet-blokkerend. | Actieve ruleset 28008175; zie bewijs hieronder. |
| BL-012 | Normaal | 0 | Gebruikersactie | Codex-evaluatieomgeving | Beschik over een geïnstalleerde, geauthenticeerde Codex CLI in een geïsoleerde toegestane omgeving zonder productiecredentials. Geen betaalde diensten zonder toestemming. | Eigenaar/toegankelijke agentomgeving. |
| BL-013 | Normaal | 0–6 | Geblokkeerd | Native gedragsevaluaties | Voer de relevante scenario's uit ACTIVATION_EVALS.md uit met de bestaande runner, beoordeel echte traces, proceduretrouw en resultaatkwaliteit, herstel regressies en registreer geschoonde resultaten. Herhaal na relevante wijzigingen en vóór Platinum-acceptatie. | BL-012; scenario's en runner bestaan al. |
| BL-014 | Later | 2–6 | Wacht op implementatie | Quality Scale-bewijsmatrix | Maak quality_scale.yaml zodra de integratiestructuur dit ondersteunt; toets alle toepasselijke criteria aan actuele officiële documentatie en koppel concrete bewijzen of gemotiveerde uitzonderingen. Geen onbewezen done-status. | Manifest en relevante implementatie/tests. |
| BL-015 | Later | 7 | Wacht op implementatie | Releasevalidatieworkflow | Automatiseer build, metadata, runtime-installatie, upgrade/verwijdering, HACS/Hassfest, tests en beveiligingspoorten; geen automatische releasepublicatie. | BL-005, BL-006; fase 1–6 en toepasselijke releasepoorten. |
| BL-016 | Later | 7 | Gebruikersactie | Marketplace-publicatietoestemming | Vraag expliciete toestemming voor concrete release, eventuele packagepublicatie en catalogusaanmelding na aantoonbaar geslaagde acceptatiecontroles. Verifieer catalogusopname pas na acceptatie en synchronisatie. | BL-005, BL-006, BL-014, BL-015; eigenaar. |
| BL-017 | Hoog | 0–7 | In uitvoering | Autonome dependencyupdates | Dagelijkse Dependabot-controles voor Actions en uv, verifieer lockfile en geslaagde update-PR's; voeg nieuwe manifesten toe zodra aanwezig. Houd Core/Python gezamenlijk op de baseline en controleer beveiligingsmeldingen; activeer veilige automatische merge pas na branchbescherming en vereiste checks. | BL-001, BL-011 voor automatische merge. |

## Actuele bewijzen en beperkingen

- BL-001: uv.lock is afkomstig uit [Baseline CI-run 45460011995](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45460011995), artifact 14951867926. De archive-hash en lockfile-hash zijn gecontroleerd. De lock bevat 178 externe packagevermeldingen, tien directe dev-requirements en 1858 gecontroleerde distributie-URL's en hashformaten. De gecommitteerde lockfile is gevalideerd via [Baseline CI-run 45460571331](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45460571331): lock-check, exacte installatie, dependencycontrole en pip-audit geslaagd. Inhoudelijke integratietests ontbreken nog.
- BL-011: [ruleset 28008175](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/rules/28008175) is actief op main; PR, actuele branch, reviewthread-resolutie en de checks Home Assistant production baseline en hassfest zijn verplicht, zonder bypass. Python-next blijft niet-blokkerend. Automatische dependency-merges zijn een afzonderlijke taak (BL-017).
- De bestaande Python-next-, Hassfest- en Marketplace-workflows zijn ingericht. Een geslaagde job met afwezige broncode of manifest betekent niet dat runtime- of integratievalidatie is uitgevoerd.
- Zeven repositoryskills, impliciete activatieconfiguratie, vijftien scenario's en een native evaluatierunner zijn aanwezig. Native gedragsevaluaties zijn nog niet uitgevoerd.
- De eerdere verzoeken om volledig tweetalige ondersteuning en autonoom documentatiebeheer zijn als BL-007 en BL-008 opgenomen; hun volledige uitwerking wordt niet als afgerond aangemerkt.
- Geen installeerbare integratie, bevestigde live API-contractvalidatie of Marketplace-toelating.

## Volgende uitvoerbare prioriteit

BL-002: configureer en valideer pre-commit in de gelockte ontwikkelomgeving. Werk onafhankelijke beleids- en documentatieonderdelen parallel af. Volg voor de daadwerkelijke implementatie de fasepoorten in het integratieplan.
