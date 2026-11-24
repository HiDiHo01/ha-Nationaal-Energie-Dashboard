---
name: project-knowledge-maintenance
description: "Select, create and improve repository skills, home-assistant.md and project guidance using verified evidence from development tasks."
---

# Skills en kennis onderhouden

Lees eerst [AGENTS.md](../../../AGENTS.md), [AI_POLICY.md](../../../AI_POLICY.md), [home-assistant.md](../../../home-assistant.md) en de relevante delen van het [integratieplan](../../../docs/INTEGRATION_PLAN.md). Deze skill verleent geen extra rechten en vervangt geen actuele primaire bronnen.

## Werkwijze

1. Lees AGENTS.md, AI_POLICY.md, home-assistant.md en de skill-index. Selecteer alle relevante skills op basis van de taak; lees hun SKILL.md vóór gebruik. Gebruik beschikbare externe skills alleen als ze relevant en toegestaan zijn.
2. Identificeer herbruikbare lessen uit code, officiële documentatie, tests en CI. Leg bron, toepasselijke baseline, datum en beperkingen vast. Geen credentials, persoonlijke data of onbevestigde API-feiten.
3. Verbeter een bestaande skill wanneer mogelijk; maak alleen een nieuwe skill bij een duidelijke terugkerende taak. Gebruik een unieke kebab-case naam die gelijk is aan de mapnaam en een korte concrete description in YAML-frontmatter.
4. Houd SKILL.md procedureel en beknopt; verwijs naar home-assistant.md, AGENTS.md en het plan voor canonieke standaarden. Voeg referenties, scripts of templates alleen toe als ze aantoonbaar nuttig en veilig zijn.
5. Valideer frontmatter, unieke namen, relatieve links, instructiehiërarchie en eventuele scripts. Controleer agents/openai.yaml op policy.allow_implicit_invocation: true en onderhoud de [activatie-evaluaties](../ACTIVATION_EVALS.md). Native gedragsevaluaties zijn optioneel (BL-012/BL-013 vervallen op eigenaarsbesluit); voer ze alleen uit na nieuwe expliciete toestemming volgens AGENTS.md en ACTIVATION_EVALS.md. Controleer bij optionele uitvoering trace en uitkomst, herstel aangetoonde regressies en rapporteer onbewezen gedrag als niet geëvalueerd, niet als faseblokkade. Een mock of statische controle is geen native bewijs.
6. Voer bij iedere taak autonoom een documentatie-impactanalyse uit volgens AGENTS.md. Werk geraakte README-versies, tweetalige changelog en gebruikershandleidingen, backlog, plan, technische referenties en skills in dezelfde PR bij. Voer de gedeelde documentatievalidator en regressietests uit; controleer daarnaast inhoudelijke pariteit, claims en bronnen. Registreer werkelijk testbewijs, ontbrekende controles en resterende blokkades.
7. Werk home-assistant.md en de index bij na relevante Core-updates, deprecations en bewezen verbeteringen. Versoepel beleid of kwaliteitscriteria niet. Commit traceerbaar en rapporteer de wijzigingen.
