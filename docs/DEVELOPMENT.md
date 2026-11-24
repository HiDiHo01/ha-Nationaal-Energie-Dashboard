# Ontwikkeling

Lees eerst [AGENTS.md](../AGENTS.md), [AI_POLICY.md](../AI_POLICY.md) en het [integratieplan](INTEGRATION_PLAN.md). Gebruik de Python-versie van de vastgelegde stabiele Home Assistant Core-baseline.

## Skills en Home Assistant-referentie

Lees [home-assistant.md](../home-assistant.md) bij Home Assistant-werkzaamheden. Gebruik de relevante [repositoryskills](../.agents/skills/README.md) door hun SKILL.md te lezen; Codex-omgevingen die repositoryskills ondersteunen kunnen ze ook automatisch ontdekken. Onderhoud beide proactief volgens AGENTS.md §1.1. De initiële skillstructuur is documentatie; daadwerkelijke selectie en effectiviteit in implementatietaken moeten nog worden geverifieerd.

Automatische skillactivatie is standaard: native impliciete selectie waar ondersteund, anders zelfstandige selectie via de skill-index. Zie de [activatie-evaluaties](../.agents/skills/ACTIVATION_EVALS.md). Native gedragsevaluaties zijn verplicht bij relevante skill- en agentwijzigingen; gebruik de geïsoleerde runner en beoordelingsprocedure in ACTIVATION_EVALS.md. De runner is met een gesimuleerde CLI gecontroleerd, niet met een echte Codex-sessie. Metadata en directe selectie zijn geen native tracebewijs.

## Compatibiliteitsbaseline

De minimale ondersteunde Home Assistant Core-versie is bij iedere nieuwe integratierelease de dan nieuwste stabiele Core-release, inclusief patchnummer. Controleer deze via https://version.home-assistant.io/stable.json en de officiële release-informatie. Gebruik een expliciete versie per release in hacs.json (homeassistant), documentatie en de reproduceerbare testomgeving; verhoog de grens pas voor een nieuwe integratierelease, niet met terugwerkende kracht. Oudere Core-versies, beta's en developmentversies hoeven niet ondersteund te worden. Valideer vóór publicatie installatie en tests tegen de vastgelegde baseline.

Huidige minimumversie: 2026.11.3. Deze versie is vastgepind in de ontwikkel- en testomgeving. De Python-doelversie volgt de major.minor-versie die de nieuwste stabiele Home Assistant Core-release gebruikt. Controleer bij het vaststellen van de Core-baseline de officiële release-tag: pyproject.toml (requires-python en toolversies) en .python-version (exacte ontwikkelversie). Neem de officiële minimale Python-versie over en pin de ontwikkelomgeving op de bijbehorende exacte Python-versie. Gebruik dezelfde major.minor-versie voor Ruff, Pylint, mypy en CI. Herbeoordeel deze waarden bij elke nieuwe integratierelease; pas oudere releases niet met terugwerkende kracht aan. Kies nooit zelfstandig een nieuwere Python-generatie dan de vastgelegde Core-baseline.

Baseline 24 november 2026: Home Assistant Core 2026.11.3, Python 3.14, upstream requires-python >=3.14.2 en ontwikkelversie 3.14.10. Bronnen: [Core pyproject.toml](https://github.com/home-assistant/core/blob/2026.11.3/pyproject.toml) en [Core .python-version](https://github.com/home-assistant/core/blob/2026.11.3/.python-version).

De repository bevat een .python-version met de exacte ontwikkelpin. Verifieer compatibiliteit van runtime en testdependencies voordat de tooling als gereed wordt gemarkeerd.

## Centrale tooling

[pyproject.toml](../pyproject.toml) bevat de projectmetadata, dev-dependencygroep en configuratie voor Ruff, Pylint, strict mypy, pytest en coverage. De root is een ontwikkelworkspace, geen distributiepackage. Versie 0.0.0 is uitsluitend de metadata van de nog niet uitgebrachte workspace. De runtime-library krijgt eigen buildmetadata in fase 1. De [synthetische runtime-wheelproef](../scripts/check_runtime_distribution.sh) is geslaagd in [Baseline CI](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45482964831/job/138760699296) op Core 2026.11.3/Python 3.14.10. Draai de proef op de exacte baseline met `bash scripts/check_runtime_distribution.sh`; de tijdelijke wheelhouse wordt zonder publicatie via de native installer gebruikt. Zie [ADR-003](ARCHITECTURE.md#adr-003--zelfstandige-wheel-via-native-requirements). Dit is geen volledige integratie-installatie.

De officiële [pytest-homeassistant](https://pypi.org/project/pytest-homeassistant/2026.11.3/) testplugin volgt Core 2026.11.3; combineer deze niet met pytest-homeassistant-custom-component. Gebruik uv met de exacte .python-version. Gebruik de gecommitteerde [uv.lock](../uv.lock). [Baseline CI-run 45460571331](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45460571331) bevestigt de lockfilecontrole, installatie op Python 3.14.10 en dependency-audit. Gebruik lokaal `uv sync --locked` met de vastgelegde Python- en uv-versie.

Na installatie van de ontwikkelomgeving en implementatie van de broncode:

```bash
ruff format --check .
ruff check .
pylint custom_components/nationaal_energie_dashboard
pylint packages/ned-api/src/ned_api
mypy
pytest --cov --cov-branch --cov-report=term-missing
pip-audit
```

De coverage-drempel bedraagt 95% voor de gecombineerde lijn- en branchdekking; de afzonderlijke branch- en modulecoverage-doelen uit het integratieplan worden aanvullend in CI bewaakt. Live contracttests zijn standaard uitgesloten. Gebruik uitsluitend voor een geautoriseerde live test `pytest -m live_api` met veilig geïnjecteerde credentials.

De TOML-syntaxis, versie-uitlijning en dependency-specifiers zijn statisch gevalideerd. Een geïsoleerde smoketest met synthetische testcode op Python 3.13.5 bevestigde async-testuitvoering, standaard uitsluiting van live_api en de 95%-coveragepoort. Dit is geen integratietest. Python 3.14.10 kon eerder niet in de lokale validatieomgeving worden geïnstalleerd. GitHub Actions heeft inmiddels de exacte Python/Core-baseline en gelockte dependencies succesvol geïnstalleerd; de broncodegebonden lint-, type- en runtimecontroles staan nog open.

De huidige structuur bevat nog geen uitvoerbare integratie of integratietests; de afzonderlijke maintenance-tests staan onder scripts/. Maak geen publieke releases zonder toestemming.

## Pre-commit en VS Code

Installeer Git, uv volgens de vastgelegde toolpin en Bash (op Windows: Git Bash of WSL). Gebruik vanuit de repository-root:

```bash
uv sync --locked
uv run --locked pre-commit install --install-hooks
uv run --locked pre-commit validate-config
uv run --locked pre-commit run --all-files
```

De eerste hookinstallatie vereist internettoegang voor de vastgepinde externe hookrepositories en hun Python-/Go-builddependencies. De root-tools komen uit uv.lock; externe hooks hebben eigen geïsoleerde omgevingen en SHA-pins. De hooks controleren JSON, YAML, TOML inclusief uv.lock, mergeconflicten, hoofdletterconflicten, regeleinden, private keys, credentialbestandsnamen, secrets in de Git-index en de lockfile. Gitleaks redigeert alle gevonden secrets en scant niet de lokale werkboom, .venv of ongevolgde bestanden. Geen volledige historiescan of garantie op afwezigheid van secrets. Los findings op; voeg geen generieke uitzonderingen toe. Ruff, Pylint en strict mypy gebruiken pyproject.toml en de gelockte tools; ze draaien zodra passende Python-broncode bestaat. Baseline CI voert dezelfde hooks uit en bewaakt daarnaast de bestaande offline tests, coverage en dependency-audit. De pre-commit-checks veranderen bestanden niet automatisch.

Open de repository-root in VS Code, installeer de aanbevolen extensies via het Extensions-paneel en selecteer de interpreter in .venv indien een eerder gekozen interpreter blijft staan. [Workspace-instellingen](../.vscode/settings.json) gebruiken de virtuele omgeving, Ruff-formattering en pytest. [Taken](../.vscode/tasks.json) bieden synchronisatie, hookinstallatie, controles, offline tests en audit via uv. Extensies kunnen eigen gebundelde tools gebruiken wanneer de omgeving ontbreekt; de gelockte CLI en CI zijn daarom leidend. De taken voor inhoudelijke tests zijn pas toepasbaar zodra tests bestaan. De instellingen zijn als JSON gecontroleerd; de grafische VS Code-omgeving is hier niet beschikbaar. [Baseline CI-run 45462898030](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45462898030) bevestigt dat pre-commit validate-config en pre-commit run --all-files met pre-commit 4.7.0 en de exacte baseline slagen: negen hooks geslaagd, zes zonder toepasselijke bestanden overgeslagen. De volledige broncodegebonden lint-, type- en testvalidatie blijft open.

## Autonoom documentatie- en taalbeheer

Volg AGENTS.md: actualiseer geraakte documentatie in dezelfde PR, inclusief [Nederlandse README](../README.md), [English README](../README.en.md), [changelog](../CHANGELOG.md), backlog, plan en relevante technische referenties. Voor nieuwe gebruikershandleidingen gebruik je gelijknamige bestanden onder docs/user/nl en docs/user/en. Beide talen moeten inhoudelijk gelijkwaardig zijn. [LICENSE](../LICENSE) blijft de canonieke licentietekst; USAGE_TERMS.md is uitsluitend een toelichting.

De [validator](../scripts/check_project_docs.py) controleert gevolgde Markdown-bestandslinks (inline en referentiedefinities, buiten eenvoudige codeblokken), documentparen en, zodra een manifest of vertaalbestand bestaat, complete niet-lege NL/EN-vertalingen met gelijke keys en placeholders. Hij verwerpt dubbele JSON-keys en niet-opgeloste Core-vertaalreferenties. Dit is een offline structurele controle, geen volledige Markdown-parser, anchorcontrole, externe linkcheck of vertaalreview. Controleer die onderdelen bij relevante wijzigingen aanvullend. Maak geen lege vertaalbestanden om CI te laten slagen.

Voer lokaal uit:

```bash
uv run --locked python scripts/check_project_docs.py
uv run --locked python -m unittest discover -s scripts -t .
uv run --locked pylint scripts
uv run --locked mypy scripts
```

Deze controles draaien ook via pre-commit in Baseline CI. De maintenance-tests zijn onafhankelijk van Home Assistant en veranderen de bestaande integratiecoveragepoort niet. Native taalgedrag en daadwerkelijke vertalingen worden in de implementatiefasen getest. De elf regressietests zijn lokaal geslaagd op Python 3.13.5 en in de eerste Baseline CI-run op de exacte baseline, waarin documentatiecontrole en strict mypy ook slagen. Ruff/Pylint vonden drie herstelbare punten; de herhaalde kwaliteitscontrole blijft open.

## Forward Compatibility Testing

- De Home Assistant/Python-baseline blijft leidend voor productiecode, linting, strict typing, volledige integratietests en de verplichte coveragepoorten.
- Onderhoud de afzonderlijke workflow python-next-smoke.yaml voor de eerstvolgende Python-major.minor-generatie (momenteel 3.15, productie 3.14). Deze experimentele job is niet releaseblokkerend (continue-on-error: true); failures blijven zichtbaar in de jobdetails. Bij een Core/Python-upgrade schuift de experimentele versie mee. Introduceer geen next-only syntax in productiecode.
- Draai op push, pull request en workflow_dispatch met alleen contents: read, zonder API-secrets of installatie van Home Assistant/het root-dev-dependencygroup.
- Controleer de volgende-versierelatie met .python-version, compileer aanwezige Python-bronnen, installeer de zelfstandige ned_api-library vanuit packages/ned-api, voer pip check en een import uit en draai offline tests/api zonder de root-coveragepoort.
- Voeg in fase 1 een zelfstandige test-extra toe aan packages/ned-api/pyproject.toml (pytest, pytest-asyncio en alle vereiste API-testdependencies, geen Home Assistant). API-tests en fixtures zijn onafhankelijk van Home Assistant; plaats noodzakelijke conftest-fixtures onder tests/api. Sluit live_api-tests uit.
- Zolang broncode of tests ontbreken, rapporteert de workflow expliciet welke controles niet zijn uitgevoerd. Een groene experimentele job is geen bewijs van volledige runtimecompatibiliteit of Platinum.

De workflow is opgeslagen in [python-next-smoke.yaml](../.github/workflows/python-next-smoke.yaml). YAML-structuur en Bash-syntaxis zijn lokaal gecontroleerd; de no-source-paden, succesvolle en mislukte syntaxcompilatie en afwijzing van een verkeerde versiebaseline zijn met synthetische bestanden en Python 3.13.5 getest. Dit is geen uitvoering op Python 3.15. De GitHub Actions-run is geslaagd; de librarytests blijven open tot de API-library bestaat.

## GitHub Actions

- Baseline CI (ci.yaml) installeert de exacte .python-version, controleert de Core- en toolversies, gebruikt uv 0.13.9 en valideert dependencies. De gecommitteerde uv.lock is verplicht; CI voert uv lock --check en uv sync --locked uit zonder regeneratie. Voeg de zelfstandige API-library met testdependencies toe aan de gelockte ontwikkelomgeving zodra deze beschikbaar is.
- Baseline CI bewaakt Ruff, Pylint, strict mypy, offline pytest, de gecombineerde coveragepoort, de afzonderlijke totale branchcoverage en de huidige modulecategorieën. Pas de coveragecontrole aan wanneer forecastberekeningen of andere kritieke modules andere bestandsnamen krijgen. Dependency-audit draait met pip-audit; kwetsbaarheden mogen niet stilzwijgend worden onderdrukt.
- Hassfest draait automatisch zodra het manifest aanwezig is; vóór dat moment wordt de ontbrekende validatie expliciet gemeld. Handmatige Hassfest-validatie vereist een manifest. Marketplace-validatie (hacs.yaml) draait handmatig en na een geautoriseerde gepubliceerde release, zonder genegeerde HACS-checks of PR-commentaar. Een echte succesvolle validatie is vereist vóór catalogusaanmelding.
- Baseline-watch controleert dagelijks de officiële Core-stablefeed en meldt afwijkingen zonder automatisch de versiegrens te wijzigen. Controleer bij de volgende release ook het upstream Python-contract. Dependabot controleert dagelijks GitHub Actions en de uv-dependencyboom (directe en indirecte dependencies, inclusief ontwikkeltools). Groepeer minor/patch-updates; beoordeel major-updates afzonderlijk. Home Assistant en pytest-homeassistant blijven gekoppeld aan de vastgelegde Core/Python-baseline en worden gezamenlijk bijgewerkt volgens §4.1–4.2. De ignore-regels gelden ook voor Dependabot-securityupdates van deze twee packages; bewaak hun kwetsbaarheden via pip-audit en upstream-beveiligingsmeldingen en behandel noodzakelijke fixes met voorrang. Houd de uv-installatieversie en andere toolpins buiten de ondersteunde manifesten actief bij; de externe pre-commit-hooks worden dagelijks door Dependabot gecontroleerd; voeg de zelfstandige API-library toe zodra haar manifest bestaat. Controleer iedere dependency-PR op herkomst, changelog, compatibiliteit, lockfile, security en toepasselijke CI. De workflow dependabot-automerge.yaml verwerkt uitsluitend geverifieerde Dependabot-minor/patchupdates voor main: geen checkout of uitvoering van PR-code, metadata en bestandscontrole met leesrechten, afzonderlijke mergejob met minimale schrijfrechten, geslaagde verplichte checks en squash-merge op de gecontroleerde head-SHA zonder bypass. Core/pytest-homeassistant, major/onbekende updates, maintainerwijzigingen, andere bestanden en de mergeworkflow zelf vereisen afzonderlijke beoordeling. Gewone workflowwijzigingen mogen alleen bestaande action-SHA's vervangen. GitHub blijft de ruleset afdwingen. De workflow gebruikt geen PAT en wacht begrensd op CI; bij failure, timeout of gewijzigde SHA wordt niet gemerged. Een GITHUB_TOKEN-merge kan opvolgende push-workflows onderdrukken; verifieer dit bij de eerste echte botmerge. Bewaar BL-017 als in uitvoering totdat echte end-to-end-validatie beschikbaar is.
- Gebruik standaard contents: read, vastgepinde action-SHA's, geen persistente checkoutcredentials en geen secrets in gewone CI. Upstream Hassfest/HACS-actions gebruiken zelf containerimages met veranderlijke tags; de action-SHA alleen maakt hun uitvoering niet volledig reproduceerbaar.
- De experimentele Python-next-job blijft afzonderlijk en niet-blokkerend. Geen automatische releases, packagepublicaties of live contractrequests. De [opt-in contractworkflow](../.github/workflows/api-contract.yaml) is voorbereid voor twee vaste dagaggregatieverzoeken in scope daily (standaard), zes tijdzoneverzoeken in scope timezone of maximaal 18 read-only requests in scope full; volg de beveiligde environment-instructies in [API_REFERENCE.md](API_REFERENCE.md). Offline unittest-tests van de probe draaien in pre-commit, zonder echte credentials of netwerk. De eigenaar heeft de beveiligde environment ingesteld en de eerste handmatige uitvoering geautoriseerd; [live-run 45469371205](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45469371205) is geslaagd. Verdere live-observaties blijven expliciet opt-in. Voeg releasevalidatie toe wanneer distributiemethode en buildvereisten beschikbaar zijn.

De vier nieuwe workflowbestanden en Dependabot-configuratie zijn lokaal als YAML geparseerd. Bash-syntaxis, ingebedde Python-syntaxis, SHA-lengtes, ontbrekende-code/lockfile-paden, Hassfest-readiness, coveragegrenzen en versieveroudering zijn met synthetische fixtures gecontroleerd op Python 3.13.5. De exacte baseline en gecommitteerde lockfile zijn op GitHub gevalideerd in [Baseline CI-run 45460571331](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45460571331). De actieve [main-ruleset](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/rules/28008175) vereist Baseline CI en hassfest vóór merge; werk via pull requests. De broncodegebonden controles zijn nog niet uitgevoerd. De eerdere [Python-next-run](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45447217991) is geslaagd; zonder API-library zijn import- en API-tests niet uitgevoerd.

## GitHub Pages

De openbare site gebruikt Jekyll 4.4.1 met Ruby 4.0.10 en Bundler 4.0.20. Gebruik site/.ruby-version, Gemfile en de gecommitteerde Gemfile.lock als bron voor de versies. De lockfile is afkomstig van [lock-resolutierun 45471790543](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45471790543) met 69 gem-checksums. Houd beide talen inhoudelijk gelijkwaardig; Markdown-pagina's onder site/nl en site/en gebruiken gedeelde layouts, includes en navigatiedata. De root is Nederlands; en.html blijft een compatibiliteitspagina.

```bash
cd site
bundle install
bundle exec jekyll serve --baseurl ""
bundle exec bundler-audit check --update
```

Installeer de vastgelegde Ruby- en Bundler-versies vooraf. CI gebruikt BUNDLE_FROZEN, controleert de lockfile, audit gems en bouwt alleen site/ met safe mode en strict front matter. De uitvoerallowlist en alle interne links worden vóór artifact-upload gecontroleerd. Externe links en browserweergave vereisen afzonderlijke controle. [Main-build en deploy](https://github.com/HiDiHo01/ha-Nationaal-Energie-Dashboard/actions/runs/45484299323) op 451152345dab6c498d5e958f62a868a7c5a463cf zijn geslaagd, inclusief gelockte gems, audit en exacte uitvoercontrole; onafhankelijke HTTPS-bereikbaarheid blijft onbevestigd. De [Pages-workflow](../.github/workflows/pages.yaml) is de enige publicatieroute; de standaard root-Jekyll-workflow is vervangen. Deploy uitsluitend main naar github-pages met minimale rechten, geen NED-secret. Settings → Pages → Source: GitHub Actions; beperk de environment tot main. Dependabot controleert Bundler dagelijks; merge gem-updates pas na review en geslaagde Pages-build en verplichte CI. Geen automatische release of cataloguspublicatie.
