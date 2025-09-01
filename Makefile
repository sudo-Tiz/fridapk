# FridAPK - APK Patcher with Frida Gadget
# Professional Docker-based Android APK patching tool

.PHONY: help venv activate install dev test lint format clean docker-safe docker-usb docker-dev docker-run docker-build

# =============================================================================
# Configuration
# =============================================================================

# Virtual environment variables
VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

# =============================================================================
# Help
# =============================================================================

help:
	@echo "FridAPK v2.0 - Available commands:"
	@echo ""
	@echo "🐍 Local Development:"
	@echo "  venv         - Create Python virtual environment"
	@echo "  install      - Install dependencies in virtual environment"
	@echo "  dev          - Setup complete development environment"
	@echo "  test         - Run basic functionality tests"
	@echo "  lint         - Run code linting (flake8)"
	@echo "  format       - Format code with Black"
	@echo "  clean        - Clean temporary files and cache"
	@echo "  clean-venv   - Remove virtual environment"
	@echo ""
	@echo "🐳 Docker Operations:"
	@echo "  docker-safe  - Run Docker container (safe mode, no USB)"
	@echo "  docker-usb   - Run Docker container (USB device access)"
	@echo "  docker-dev   - Run Docker container (development mode)"
	@echo "  docker-run   - One-shot Docker run with custom args"
	@echo "  docker-build - Build Docker image locally"
	@echo ""
	@echo "📖 Usage Examples:"
	@echo "  make docker-safe                    # Interactive container"
	@echo "  make docker-run ARGS='-a app.apk'  # Direct command"
	@echo "  make docker-dev                     # Development with mounted source"

# =============================================================================
# Local Development
# =============================================================================

venv:
	@echo "🐍 Creating Python virtual environment..."
	@if [ ! -d "$(VENV)" ]; then \
		python3 -m venv $(VENV); \
		echo "✅ Virtual environment created."; \
	else \
		echo "ℹ️  Virtual environment already exists."; \
	fi

install: venv
	@echo "📦 Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "✅ Dependencies installed."

dev: venv
	@echo "🔧 Setting up development environment..."
	@# Enable development dependencies (uncomment lines starting with #)
	sed -i 's/^#\([^[:space:]]\)/\1/' requirements.txt
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(VENV)/bin/pre-commit install
	@echo "✅ Development environment ready."

test: venv
	@echo "🧪 Running basic tests..."
	$(PYTHON) fridapk --help
	$(PYTHON) -m py_compile fridapk
	find src/ -name "*.py" -exec $(PYTHON) -m py_compile {} \; 2>/dev/null || true
	@echo "✅ Basic tests completed."

lint: venv
	@echo "🔍 Running code linting..."
	$(VENV)/bin/flake8 --max-line-length=88 --ignore=E203,W503 src/ fridapk || true
	@echo "ℹ️  Linting completed."

format: venv
	@echo "🎨 Formatting code..."
	$(VENV)/bin/black --line-length=88 src/ fridapk || true
	@echo "✅ Code formatted."

clean:
	@echo "🧹 Cleaning temporary files..."
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -rf .pytest_cache/
	@echo "✅ Cleanup completed."

clean-venv:
	@echo "🗑️  Removing virtual environment..."
	rm -rf $(VENV)
	@echo "✅ Virtual environment removed."

# =============================================================================
# Docker Operations
# =============================================================================

docker-safe:
	@echo " Starting Docker container (safe mode)..."
	docker-compose run --rm fridapk-safe

docker-usb:
	@echo "🐳 Starting Docker container (USB mode)..."
	docker-compose run --rm fridapk-usb

docker-dev:
	@echo "🐳 Starting Docker container (development mode)..."
	@echo "ℹ️  Source code will be mounted for live editing"
	docker-compose run --rm fridapk-dev

docker-run:
	@echo "🐳 Running Docker container (one-shot mode)..."
	@if [ -z "$(ARGS)" ]; then \
		echo "ℹ️  Starting interactive shell..."; \
		docker run -it --rm -v $(PWD)/workspace:/workspace ghcr.io/sudo-tiz/fridapk:latest bash; \
	else \
		echo "ℹ️  Running: fridapk $(ARGS)"; \
		docker run -it --rm -v $(PWD)/workspace:/workspace ghcr.io/sudo-tiz/fridapk:latest fridapk $(ARGS); \
	fi

docker-build:
	@echo "🐳 Building Docker image..."
	@echo "ℹ️  This may take several minutes on first build..."
	docker build -t fridapk-local .
	@echo "✅ Docker image built successfully."
