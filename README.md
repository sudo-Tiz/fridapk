# FridAPK

> **🔥 Automatically patch Android APKs with Frida Gadget**

FridAPK is a powerful tool that automates the injection of Frida Gadget into Android APKs, enabling dynamic analysis and reverse engineering without root access. Built with modern Python architecture and professional development tools.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Frida](https://img.shields.io/badge/Frida-Dynamic%20Analysis-red.svg)](https://frida.re/)
[![Code Quality](https://img.shields.io/badge/code%20quality-ruff-blue.svg)](https://github.com/astral-sh/ruff)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen.svg)](https://github.com/pre-commit/pre-commit)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://hub.docker.com/)

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔄 **Automatic Frida Gadget injection** | No more manual patching - fully automated |
| 📱 **Device architecture detection** | Auto-selects the right gadget for target device |
| 🔐 **User certificate authorities** | Bypass certificate pinning with custom CAs |
| 📜 **Auto-load JavaScript hooks** | Embed and execute scripts directly in APK |
| ✍️ **APK signing and alignment** | Production-ready output with proper signatures |
| 🐳 **Docker support** | Zero-dependency containerized environment |
| 🛠️ **Modern development tools** | Pre-commit hooks, Ruff linting, automated formatting |
| ⚙️ **Modular architecture** | Clean, maintainable codebase with src/core structure |

## 🚀 Quick Start

### Method 1: Docker (Recommended)

```bash
# Patch an APK instantly - zero setup required
docker run -it --rm -v $(pwd):/workspace ghcr.io/sudo-tiz/fridapk:latest fridapk -a /workspace/app.apk
```

### Method 2: Docker Compose

```bash
git clone https://github.com/sudo-Tiz/fridapk
cd fridapk

make docker-safe   # Interactive safe mode
make docker-usb    # Interactive USB mode

# Or one-shot commands
make docker-run ARGS="-a /workspace/app.apk"
```

### Method 3: Local Installation

```bash
git clone https://github.com/sudo-Tiz/fridapk
cd fridapk

# Option A: Virtual environment (recommended)
make install && source .venv/bin/activate
fridapk -a app.apk

# Option B: System-wide pip install
pip install -r requirements.txt
./fridapk -a app.apk

# Option C: Development setup
make dev  # Includes pre-commit hooks and development tools
```

## 📖 Usage

### Basic Commands

```bash
# Patch APK with auto-detected gadget
fridapk -a app.apk

# Use specific gadget
fridapk -a app.apk -g /path/to/gadget.so

# Enable user certificates (bypass SSL pinning)
fridapk -a app.apk --enable-user-certs

# Auto-load JavaScript hook
fridapk -a app.apk --autoload-script hook.js
```

### Docker Usage

```bash
# Interactive shell with docker-compose
make docker-safe   # Opens interactive bash in safe mode
make docker-usb    # Opens interactive bash with USB access

# One-shot patching
make docker-run ARGS="-a /workspace/app.apk"

# Direct docker run
docker run -it --rm -v $(pwd)/workspace:/workspace ghcr.io/sudo-tiz/fridapk:latest fridapk -a /workspace/app.apk
```

## 🛠️ Advanced Options

| Option | Description | Example |
|--------|-------------|---------|
| `--output` | Output file path | `fridapk -a app.apk -o patched.apk` |
| `--gadget` | Specific gadget file | `fridapk -a app.apk -g ./gadget.so` |
| `--autoload-script` | JavaScript file to auto-load | `fridapk -a app.apk --autoload-script hook.js` |
| `--enable-user-certs` | Enable user certificate authorities | `fridapk -a app.apk --enable-user-certs` |
| `--prevent-gadget` | Skip Frida gadget injection | `fridapk -a app.apk --prevent-gadget` |
| `--force-resources` | Force resource extraction | `fridapk -a app.apk --force-resources` |
| `--keep-keystore` | Keep generated keystore | `fridapk -a app.apk --keep-keystore` |
| `--wait` | Wait before repackaging | `fridapk -a app.apk --wait` |
| `--verbosity` | Verbosity level (1-3) | `fridapk -a app.apk -v 3` |

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FRIDAPK_TEMP_DIR` | Temporary files directory | `/tmp/fridapk` |
| `FRIDAPK_GADGETS_DIR` | Gadgets cache directory | `/fridapk/gadgets` |
| `FRIDAPK_KEYSTORE_PATH` | Custom keystore location | Auto-generated |

### Gadget Management

```bash
# Update gadget cache
fridapk --update-gadgets

# List available gadgets
fridapk --list-gadgets

# Use specific gadget version
fridapk -a app.apk --gadget-version 16.1.4
```

## 🎯 Use Cases & Examples

### SSL Pinning Bypass
```bash
# Enable user certificates to bypass SSL pinning
fridapk -a app.apk --enable-user-certs
```

### JavaScript Hook Injection
```bash
# Create hook script
echo 'Java.perform(() => { console.log("Hooked!"); });' > hook.js

# Inject and auto-load the hook
fridapk -a app.apk --autoload-script hook.js
```

### Advanced Patching Workflow
```bash
# Full workflow with custom output and debugging
fridapk -a app.apk \
  --output patched-app.apk \
  --enable-user-certs \
  --autoload-script debug-hooks.js \
  --keep-keystore \
  --verbosity 3
```

### Docker Workflows
```bash
# Safe mode (no USB devices)
make docker-safe

# USB mode (device debugging)
make docker-usb

# Development mode (live code editing)
make docker-dev

# One-shot with custom arguments
make docker-run ARGS="--help"
```

## 🔧 Development

### Quick Setup
```bash
make help    # Show all available commands
make dev     # Setup development environment with pre-commit hooks
make test    # Run basic functionality tests
make lint    # Run all code quality checks (pre-commit)
make format  # Format code with Ruff
make check   # Quick local checks with Ruff (no auto-fix)
```

### Development Tools
| Tool | Purpose | Configuration | Benefits |
|------|---------|---------------|----------|
| **Ruff** | Linting + Formatting | `pyproject.toml` | 10-100x faster than flake8, all-in-one |
| **Pre-commit** | Git hooks | `.pre-commit-config.yaml` | Automatic code quality checks |
| **isort** | Import sorting | Integrated with Ruff | Consistent import organization |
| **Docker** | Containerization | `docker-compose.yml` | Isolated development environment |

## 🚨 Security Warnings
- **Legal Compliance**: Only use on applications you own or have explicit permission to analyze
- **Shell Commands**: FridAPK executes shell commands - verify input sources
- **Temporary Files**: Sensitive data may be temporarily stored in `/tmp/fridapk`

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Quick Contribution Guide
```bash
# Fork the repository and clone
git clone https://github.com/YOUR_USERNAME/fridapk
cd fridapk

# Setup development environment
make dev

# Make your changes and test
make test lint

# Commit will automatically run pre-commit hooks
git commit -m "feat: your awesome feature"

# Push and create PR
git push origin feature-branch
```

### Contribution Standards
| Aspect | Requirement |
|--------|-------------|
| **Code Quality** | Pre-commit hooks must pass |
| **Testing** | Basic functionality tests required |
| **Documentation** | Update README for new features |
| **Commit Style** | Use conventional commits format |

## 🐛 Troubleshooting

### Common Issues & Solutions

| Issue | Solution | Command |
|-------|----------|---------|
| **Missing dependencies** | Update gadgets cache | `fridapk --update-gadgets` |
| **Permission denied** | Check file permissions | `chmod +x fridapk` |
| **Device not detected** | Verify ADB connection | `adb devices` |
| **APK parsing errors** | Check APK integrity | `aapt dump badging app.apk` |
| **Signature issues** | Use keep-keystore option | `fridapk -a app.apv --keep-keystore` |

### Development Issues
```bash
# Reset development environment
make clean-venv && make dev

# Quick local code checks
make check

# Full quality checks (all pre-commit hooks)
make lint

# Check pre-commit status
pre-commit run --all-files

# Verify Python syntax
python -m py_compile fridapk
```

## 📝 License

GCU License - see [LICENSE](LICENSE) file for details.

---

**⭐ If FridAPK helps you, please star this repository!**
