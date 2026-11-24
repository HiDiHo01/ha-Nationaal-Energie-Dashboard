# Architectuur

De technische baseline staat in [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md), hoofdstukken 4–11.

- Home Assistant-entiteiten lezen getypeerde coordinator-snapshots.
- Current en forecast hebben afzonderlijke coordinators; historie is on-demand.
- De zelfstandige NED-library beheert HTTP, authenticatie, parsing en requestbudget.
- De runtime gebruikt een geïnjecteerde aiohttp-sessie.
- De Marketplace installeert één integratiemap; valideer in fase 0 hoe de zelfstandige library reproduceerbaar beschikbaar wordt gemaakt zonder ontwikkelaarscheckout.

Status: ontwerp, nog niet geïmplementeerd.
