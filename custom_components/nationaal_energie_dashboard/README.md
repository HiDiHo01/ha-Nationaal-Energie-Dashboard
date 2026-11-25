# Home Assistant-runtime

Domain: nationaal_energie_dashboard. Deze map wordt de installatieroot voor Home Assistant. Fase 2 levert manifest, setup/unload, configuratie en coordinators; fase 3 sensors en vertalingen; fase 4 actions; fase 5 diagnostiek.

Alle runtimebestanden moeten bij Marketplace-installatie beschikbaar zijn. De negen gevraagde integratiebestanden zijn als ontwikkelconcept geschreven. De API-keyflow maskeert de sleutel; de entry en provider zijn geblokkeerd tot de toepasselijke contractvoorwaarden en de definitieve runtime-client zijn gevalideerd. Het manifest is uitsluitend voor offline ontwikkeling (0.0.0.dev0, nog geen externe runtime-requirements). Geen installeerbare productie-integratie of faseacceptatie. De acht sensoren gebruiken genormaliseerde snapshots; de huidige stalenessgrens van 30 minuten is een voorlopige ontwerpwaarde, geen bewezen NED-contract. Zie [integratieplan](../../docs/INTEGRATION_PLAN.md).

Drie handmatig gerapporteerde authenticatieproeven bevestigen voor dezelfde nationale zonnequery HTTP 200 (geldige key), 401 (ontbrekend) en 403 (ongeldig). De verondersteld beperkte key krijgt toegang; rechtensemantiek blijft open. De conceptclient en Config Flow onderscheiden 401 van 403 zonder foutpayloads te loggen; de live koppeling blijft geblokkeerd.

De Config Flow-adapter is nu werkelijk verbonden met de onafhankelijke authenticatieclient via de Core-sessie. De expliciete readiness guard blijft gesloten; alleen offline regressietests vervangen die guard en het transport. De productieprovider blijft geblokkeerd. De scannerbevindingen voor vaste sensor-ID's zijn door semantisch equivalente code aangepakt; geen wijziging aan de acht unique IDs.
