.PHONY: setup lint test test-unit test-openapi test-integration dev web-setup web-dev web-build web-lint web-e2e crawler-setup crawler-ingest crawler-daily crawler-weekly crawler-summary crawler-test

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

web-setup:
	cd apps/web && npm install

web-dev:
	cd apps/web && npm run dev

web-build:
	cd apps/web && npm run build

web-lint:
	cd apps/web && npm run lint

web-e2e:
	cd apps/web && npm run test:e2e

crawler-setup:
	python3 -m pip install -r apps/crawler/requirements.txt

crawler-ingest:
	PYTHONPATH=apps/crawler python3 -m crawler.cli ingest-all

crawler-daily:
	python3 apps/crawler/scripts/run_daily.py

crawler-weekly:
	python3 apps/crawler/scripts/run_weekly.py

crawler-summary:
	PYTHONPATH=apps/crawler python3 -m crawler.cli summary

crawler-test:
	PYTHONPATH=apps/crawler python3 -m pytest -q apps/crawler/tests
