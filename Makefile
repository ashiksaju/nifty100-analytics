PYTHON = python

load:
	$(PYTHON) src/etl/loader.py

validate:
	$(PYTHON) src/etl/validator.py

ratios:
	$(PYTHON) src/analytics/financial_ratios.py

test:
	pytest tests/

report:
	$(PYTHON) src/reports/generate_report.py

dashboard:
	@echo "Open the Power BI dashboard manually."

api:
	@echo "API module will be added in a later sprint."

clean:
	@echo "Cleaning temporary files..."
	@if exist __pycache__ rmdir /s /q __pycache__
	@if exist .pytest_cache rmdir /s /q .pytest_cache