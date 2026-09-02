.PHONY: test test-functional test-security test-contract test-load run-tests up down

test:
	@mkdir -p reports
	@docker compose up -d --build api
	@status=0; docker compose run --build --rm tests || status=$$?; docker compose down; exit $$status

test-functional:
	@$(MAKE) run-tests PYTEST_ARGS="-m functional"

test-security:
	@$(MAKE) run-tests PYTEST_ARGS="-m security"

test-contract:
	@$(MAKE) run-tests PYTEST_ARGS="-m contract"

test-load:
	@$(MAKE) run-tests PYTEST_ARGS="-m load --junitxml=reports/load-junit.xml --html=reports/load-report.html --self-contained-html"

run-tests:
	@mkdir -p reports
	@docker compose up -d --build api
	@status=0; docker compose run --build --rm tests pytest $(PYTEST_ARGS) || status=$$?; docker compose down; exit $$status

up:
	@docker compose up -d api

down:
	@docker compose down
