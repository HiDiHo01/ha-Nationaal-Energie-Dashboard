# Repositoryskills

Deze map bevat projectgebonden, herbruikbare Agent Skills. Elke skill heeft een eigen map met SKILL.md en YAML-frontmatter (name en description). De mapindeling volgt de [Codex-repositoryconventie](https://developers.openai.com/blog/skills-agents-sdk). Gebruik skills ook door de relevante bestanden rechtstreeks te lezen wanneer de agentomgeving ze niet automatisch ontdekt.

| Skill | Toepassing |
| --- | --- |
| [ha-integration](ha-integration/SKILL.md) | Implement or review Home Assistant config flows, lifecycle, coordinators, entities, actions, translations and migrations. |
| [ned-api-contract](ned-api-contract/SKILL.md) | Verify NED API specifications, datasets, authentication, response parsing, pagination, retry limits and standalone client changes. |
| [energy-data-semantics](energy-data-semantics/SKILL.md) | Validate energy, power, CO2, forecast, interval aggregation, statistics and DST semantics for NED datasets. |
| [ha-quality-verification](ha-quality-verification/SKILL.md) | Verify Python and Home Assistant code changes with Ruff, Pylint, strict mypy, pytest, coverage, security and Quality Scale evidence. |
| [ci-workflow-maintenance](ci-workflow-maintenance/SKILL.md) | Design, repair and maintain GitHub Actions, lockfiles, dependency audits and forward compatibility workflows. |
| [marketplace-readiness](marketplace-readiness/SKILL.md) | Review Home Assistant Marketplace admission, HACS and Hassfest, metadata, branding, package installation and release preparation. |
| [project-knowledge-maintenance](project-knowledge-maintenance/SKILL.md) | Select, create and improve repository skills, home-assistant.md and project guidance using verified evidence from development tasks. |

Lees de relevante skills bij aanvang, combineer ze waar nodig en onderhoud ze volgens [AGENTS.md](../../AGENTS.md) en [project-knowledge-maintenance](project-knowledge-maintenance/SKILL.md). Geen automatische installatie van externe skills, geen duplicatie van beleid en geen secrets in skills. Nieuwe skills worden pas toegevoegd aan deze index na validatie.
