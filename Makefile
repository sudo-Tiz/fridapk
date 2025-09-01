.PHONY: help venv install dev test lint format clean docker-safe docker-usb

# Virtual environment variables
VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

help:
	@echo "FridAPK - Available commands:"
	@echo "  venv        - Create virtual environment"
	@echo "  install     - Install dependencies"
	@echo "  dev         - Setup development environment"
	@echo "  test        - Run basic tests"
	@echo "  lint        - Run code linting"
	@echo "  format      - Format code"
	@echo "  clean       - Clean temporary files"
	@echo "  clean-venv  - Remove virtual environment"
	@echo "  docker-safe - Run Docker safe mode"
	@echo "  docker-usb  - Run Docker USB mode"

venv:
	@if [ ! -d "$(VENV)" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv $(VENV); \
		echo "Virtual environment created. Activate with: source $(VENV)/bin/activate"; \
	else \
		echo "Virtual environment already exists."; \
	fi

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

dev: venv
	sed -i 's/^#\([^[:space:]]\)/\1/' requirements.txt
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(VENV)/bin/pre-commit install

test: venv
	$(PYTHON) fridapk --help
	$(PYTHON) -m py_compile fridapk
	find src/ -name "*.py" -exec $(PYTHON) -m py_compile {} \; 2>/dev/null || true

lint: venv
	$(VENV)/bin/flake8 --max-line-length=88 --ignore=E203,W503 src/ fridapk || true

format: venv
	$(VENV)/bin/black --line-length=88 src/ fridapk || true

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -rf .pytest_cache/

clean-venv:
	rm -rf $(VENV)
	@echo "Virtual environment removed."

docker-safe:
	docker-compose up fridapk-safe

docker-usb:
	docker-compose up fridapk-usb
