# API-tests

Test de onafhankelijke NED-library met gemockte HTTP-responses, inclusief authenticatie, parsing, paginering, retries, rate limiting, cancellation en DST. Live contracttests zijn opt-in; gebruik veilig geïnjecteerde credentials.

De eerste synthetische tests in [test_exceptions.py](test_exceptions.py) toetsen alle acht specifieke exceptiontypes en de gemeenschappelijke basis. Draai de gelockte baseline vanuit de repository-root met `uv run --locked pytest tests/api --cov=ned_api --cov-branch --cov-report=term-missing`; de volledige baseline-CI blijft leidend voor alle coveragepoorten.
