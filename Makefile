.PHONY: setup lint test test-unit test-openapi test-integration dev

setup:
	python3 -m pip install -r apps/api/requirements.txt

lint:
	PYTHONPATH=apps/api python3 -m ruff check apps/api/app apps/api/tests

test:
	$(MAKE) test-openapi
	$(MAKE) test-integration
	$(MAKE) test-unit

test-unit:
	PYTHONPATH=apps/api python3 -m pytest -q apps/api/tests/test_matches.py apps/api/tests/test_stats_teams.py

test-openapi:
	PYTHONPATH=apps/api python3 -m pytest -q apps/api/tests/test_openapi_snapshot.py

test-integration:
	PYTHONPATH=apps/api python3 -m pytest -q apps/api/tests/test_integration_api_002_005.py

dev:
	PYTHONPATH=apps/api python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
