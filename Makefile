.PHONY: help install install-dev test test-cov lint format clean build publish

help: ## Show this help message
	@echo "File Difference Analyzer - Development Commands"
	@echo "=============================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package in development mode
	pip install -e .

install-dev: ## Install the package with development dependencies
	pip install -e .[dev]

test: ## Run tests
	python -m pytest tests/ -v

test-cov: ## Run tests with coverage
	python -m pytest tests/ --cov=file_diff_analyzer --cov-report=html --cov-report=term-missing

lint: ## Run linting checks
	flake8 src/ tests/
	mypy src/

format: ## Format code with black
	black src/ tests/

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: ## Build the package
	python setup.py sdist bdist_wheel

publish: ## Publish to PyPI (requires twine)
	twine upload dist/*

check-build: ## Check build artifacts
	twine check dist/*

install-all-formats: ## Install with all format support
	pip install -e .[all]

run-examples: ## Run example scripts
	python examples/basic_usage.py
	python examples/universal_analysis.py

check-deps: ## Check for outdated dependencies
	pip list --outdated

update-deps: ## Update dependencies to latest versions
	pip install --upgrade -r requirements.txt

docs: ## Generate documentation
	cd docs && make html

install-test-deps: ## Install test dependencies only
	pip install pytest pytest-cov black flake8 mypy

quick-test: ## Run quick tests only
	python -m pytest tests/ -x -v --tb=short

test-slow: ## Run only slow tests
	python -m pytest tests/ -m slow -v

test-unit: ## Run only unit tests
	python -m pytest tests/ -m unit -v

test-integration: ## Run only integration tests
	python -m pytest tests/ -m integration -v
