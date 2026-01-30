# Makefile for Satellite Data Acquisition development tasks
# Author: Peter Kongstad

.PHONY: help install install-dev install-uv install-dev-uv test test-fast test-cov lint format check clean pre-commit docker docker-build docker-run

help:
	@echo "Satellite Data Acquisition Development Commands"
	@echo "==============================================="
	@echo ""
	@echo "Setup (UV - Recommended):"
	@echo "  make install-uv       Install package with UV (fast!)"
	@echo "  make install-dev-uv   Install with dev dependencies using UV"
	@echo ""
	@echo "Setup (pip):"
	@echo "  make install          Install package and dependencies"
	@echo "  make install-dev      Install with development dependencies"
	@echo "  make pre-commit       Install pre-commit hooks"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     Build Docker image"
	@echo "  make docker-run       Run Docker container interactively"
	@echo "  make docker-test      Run tests in Docker"
	@echo ""
	@echo "Testing:"
	@echo "  make test            Run all tests"
	@echo "  make test-fast       Run fast tests only (no integration)"
	@echo "  make test-cov        Run tests with coverage report"
	@echo "  make test-verbose    Run tests with verbose output"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint            Run all linters"
	@echo "  make format          Auto-format code with black and isort"
	@echo "  make check           Run format check without modifying"
	@echo "  make type-check      Run mypy type checking"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean           Remove build artifacts and cache"
	@echo "  make clean-data      Remove test data outputs"

install:
	pip install -e .

install-dev:
	pip install -e .
	pip install pytest ruff black pre-commit ipykernel tbump

install-uv:
	uv pip install -e .

install-dev-uv:
	uv pip install -e .
	uv pip install pytest ruff black pre-commit ipykernel tbump

pre-commit:
	pre-commit install

docker-build:
	docker build -t sat-data-acquisition .

docker-run:
	docker run -it -v $$(pwd)/data:/app/data sat-data-acquisition bash

docker-test:
	docker run sat-data-acquisition pytest

test:
	pytest

test-fast:
	pytest -m "not slow and not integration"

test-cov:
	pytest --cov=sat_data_acquisition --cov-report=html --cov-report=term

test-verbose:
	pytest -vv

lint:
	@echo "Running ruff check..."
	ruff check sat_data_acquisition tests
	@echo "Running flake8..."
	flake8 --max-line-length=100 sat_data_acquisition tests
	@echo "Running mypy..."
	mypy sat_data_acquisition

format:
	@echo "Running black..."
	black sat_data_acquisition tests
	@echo "Running isort..."
	isort sat_data_acquisition tests

check:
	@echo "Checking black..."
	black --check sat_data_acquisition tests
	@echo "Checking isort..."
	isort --check-only sat_data_acquisition tests

type-check:
	mypy sat_data_acquisition

clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

clean-data:
	@echo "Cleaning test data..."
	rm -rf data/batch_test
	rm -rf data/multi_image_test
	find . -name "*.tif" -type f -delete
	find . -name "*.npy" -type f -delete
