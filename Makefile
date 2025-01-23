.PHONY: all clean install test coverage coverage-html
.PHONY: test-vcon test-pydantic coverage-vcon coverage-pydantic

# Default target
all: clean install test

# Clean up build artifacts and other crap
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

# Install deps
install:
	poetry install
	cd vcon-pydantic && poetry install

# testing
test-vcon:
	poetry run pytest tests/

test-pydantic:
	cd vcon-pydantic && poetry run pytest

test: test-vcon test-pydantic
	@echo "All tests completed"

# testing with coverage yay
coverage-vcon:
	poetry run pytest --cov=vcon --cov-report=term-missing tests/

coverage-pydantic:
	cd vcon-pydantic && poetry run pytest --cov=src --cov-report=term-missing tests/

coverage: coverage-vcon coverage-pydantic
	@echo "All coverage reports completed"