# Home Assistant-runtime

Domain: nationaal_energie_dashboard. Beperkte lokale alpha 0.1.0a1, uitsluitend vijf nationale current-capacity-datasets. Reviewherstel R39-01–08: status-first foutafhandeling, Retry-After, budget per HTTP-poging, afzonderlijke datasetbeschikbaarheid en ontvangsttijd. Gebruik de gecontroleerde lokale launcher voor de aparte testomgeving. De native lifecycle- en wheelpreflighttests moeten op de definitieve commit slagen. Geen nieuwe live probes of release.

Eén currentcoordinator, Core-sessiefactory met native SSRF en aanvullende attempt-middleware, proceslokaal budget. HTTP 401/429 blokkeert de batch; afzonderlijke 403/response-/transportfouten isoleren datasets, loggen alleen geschoonde overgangscontext en herstellen bij succesvolle volgende refresh. Alle datasets mislukt leidt tot een native updatefout. Alleen bij requestaanvang en ontvangst gesloten kwartieren; geen nulvulling, revisieselectie of automatische promotie van open intervallen. CO₂, forecast en hernieuwbaar aandeel blijven gereserveerd.

Zie [reviewregistratie](../../docs/PR39_REVIEW.md), [NL](../../docs/user/nl/alpha-test.md) en [EN](../../docs/user/en/alpha-test.md) lokale testinstructies. Geen productie-installatie of faseacceptatie.

R39-09–12 en CodeRabbit: periodieke polling uitsluitend voor actieve entity-contexten (eerste refresh alle vijf), halfopen 30-minutenvenster, geen herstelmelding zonder vers gesloten kwartier; alle actieve datasets zonder bruikbare waarde geven een updatefout en bij setup een native retry. HTTP asctime-date wordt als UTC verwerkt volgens RFC 9110 §5.6.7. De launcherproef gebruikt een tijdelijke venv met minimale localhost-HTTP-configuratie, geen NED-entry of sleutel; volledige frontend- en eigenaarstest blijven open.
