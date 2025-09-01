# FridAPK Makefile - DRY & KISS

.PHONY: help venv install dev test lint check clean docker-safe docker-usb docker-dev docker-run docker-build

# Variables
VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

# Common functions
define install-deps
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
endef

help:
	@echo "🔥 FridAPK - Available commands:"
	@echo ""
	@echo "🐍 Local Development:"
	@echo "  venv         - Create Python virtual environment"
	@echo "  install      - Install dependencies in virtual environment"
	@echo "  dev          - Setup complete development environment"
	@echo "  test         - Run basic functionality tests"
	@echo "  lint         - Run all code quality checks and formatting"
	@echo "  check        - Quick Ruff checks (no auto-fix)"
	@echo "  clean        - Clean temporary files and cache"
	@echo ""
	@echo "🐳 Docker Operations:"
	@echo "  docker-safe  - Run Docker container (safe mode, no USB)"
	@echo "  docker-usb   - Run Docker container (USB device access)"
	@echo "  docker-dev   - Run Docker container (development mode)"
	@echo "  docker-run   - One-shot Docker run with custom args"
	@echo "  docker-build - Build Docker image locally"

venv:
	@[ -d "$(VENV)" ] || python3 -m venv $(VENV)

install: venv
	$(call install-deps)

dev: venv
	$(call install-deps)
	$(PIP) install -r requirements-dev.txt
	$(VENV)/bin/pre-commit install

test: venv
	$(PYTHON) fridapk --help >/dev/null
	$(PYTHON) -m py_compile fridapk
	find src/ -name "*.py" -exec $(PYTHON) -m py_compile {} \; 2>/dev/null

lint: venv
	$(VENV)/bin/pre-commit run --all-files

check: venv
	$(VENV)/bin/ruff check src/ fridapk
	$(VENV)/bin/ruff format src/ fridapk --check

clean:
	find . -name "*.pyc" -delete -o -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache/

# Docker shortcuts
docker-safe:
	docker-compose run --rm fridapk-safe

docker-usb:
	docker-compose run --rm fridapk-usb

docker-dev:
	docker-compose run --rm fridapk-dev

docker-run:
	@if [ -z "$(ARGS)" ]; then \
		docker run -it --rm -v $(PWD)/workspace:/workspace ghcr.io/sudo-tiz/fridapk:latest bash; \
	else \
		docker run -it --rm -v $(PWD)/workspace:/workspace ghcr.io/sudo-tiz/fridapk:latest fridapk $(ARGS); \
	fi

docker-build:
	docker build -t fridapk-local .
