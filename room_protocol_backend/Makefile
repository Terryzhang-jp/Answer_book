.PHONY: help install install-dev test test-unit test-integration coverage lint format type-check clean run

help:
	@echo "Available commands:"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo "  test         Run all tests"
	@echo "  test-unit    Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  coverage     Run tests with coverage report"
	@echo "  lint         Run code linting"
	@echo "  format       Format code with black and isort"
	@echo "  type-check   Run type checking with mypy"
	@echo "  clean        Clean up cache files"
	@echo "  run          Start the development server"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pre-commit install

test:
	pytest

test-unit:
	pytest tests/unit/

test-integration:
	pytest tests/integration/

coverage:
	pytest --cov=. --cov-report=html --cov-report=term

lint:
	flake8 .

format:
	black .
	isort .

type-check:
	mypy .

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/

run:
	python main.py

# Development workflow
dev-setup: install-dev
	@echo "Development environment setup complete!"

dev-check: format lint type-check test
	@echo "All development checks passed!"
