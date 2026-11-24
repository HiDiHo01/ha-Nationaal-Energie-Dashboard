# Home Assistant-runtime

Domain: nationaal_energie_dashboard. Deze map wordt de installatieroot voor Home Assistant. Fase 2 levert manifest, setup/unload, configuratie en coordinators; fase 3 sensors en vertalingen; fase 4 actions; fase 5 diagnostiek.

Alle runtimebestanden moeten bij Marketplace-installatie beschikbaar zijn. De negen gevraagde integratiebestanden zijn als ontwikkelconcept geschreven. De API-keyflow maskeert de sleutel; de entry en provider zijn geblokkeerd tot de toepasselijke contractvoorwaarden en de definitieve runtime-client zijn gevalideerd. Het manifest is uitsluitend voor offline ontwikkeling (0.0.0.dev0, nog geen externe runtime-requirements). Geen installeerbare productie-integratie of faseacceptatie. De acht sensoren gebruiken genormaliseerde snapshots; de huidige stalenessgrens van 30 minuten is een voorlopige ontwerpwaarde, geen bewezen NED-contract. Zie [integratieplan](../../docs/INTEGRATION_PLAN.md).
