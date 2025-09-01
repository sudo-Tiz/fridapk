# FridAPK

> **🔥 Automatically patch Android APKs with Frida Gadget**

FridAPK is a powerful tool that automates the injection of Frida Gadget into Android APKs, enabling dynamic analysis and reverse engineering without root access.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Frida](https://img.shields.io/badge/Frida-Dynamic%20Analysis-red.svg)](https://frida.re/)
[![CI](https://github.com/sudo-Tiz/fridapk/workflows/CI/badge.svg)](https://github.com/sudo-Tiz/fridapk/actions)
[![Release](https://github.com/sudo-Tiz/fridapk/workflows/Release/badge.svg)](https://github.com/sudo-Tiz/fridapk/releases)

## ✨ Features

- 🔄 **Automatic Frida Gadget injection** - No more manual patching
- 📱 **Device architecture detection** - Auto-selects the right gadget
- 🔐 **User certificate authorities support** - Bypass certificate pinning
- 📜 **Auto-load JavaScript hooks** - Embed scripts directly in APK
- ✍️ **APK signing and alignment** - Production-ready output
- 🐳 **Docker support** - Zero-dependency environment

## 🚀 Quick Start

### Instant usage (no installation)

```bash
# Patch an APK instantly - zero setup required
docker run -it --rm -v $(pwd):/workspace ghcr.io/sudo-tiz/fridapk:latest fridapk -a /workspace/app.apk
```

### Docker Compose

```bash
git clone https://github.com/sudo-Tiz/fridapk
cd fridapk

make docker-safe   # Safe mode (no USB)
make docker-usb    # USB access mode
```

### Local Installation

```bash
git clone https://github.com/sudo-Tiz/fridapk
cd fridapk

# With virtual environment (recommended)
make install && source .venv/bin/activate

# Or system-wide
pip install -r requirements.txt && chmod +x fridapk
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
# Using docker-compose
docker-compose exec fridapk-safe fridapk -a /home/fridapk/workspace/app.apk

# Direct docker run
docker run -it --rm -v $(pwd):/workspace ghcr.io/sudo-tiz/fridapk:latest fridapk -a /workspace/app.apk

# With USB access for device detection
docker run -it --rm --privileged -v /dev/bus/usb:/dev/bus/usb -v $(pwd):/workspace ghcr.io/sudo-tiz/fridapk:latest
```

## 🛠️ Advanced Options

| Option | Description |
|--------|-------------|
| `--output` | Output file path |
| `--gadget` | Specific gadget file |
| `--autoload-script` | JavaScript file to auto-load |
| `--enable-user-certs` | Enable user certificate authorities |
| `--prevent-gadget` | Skip Frida gadget injection |
| `--force-resources` | Force resource extraction |
| `--keep-keystore` | Keep generated keystore |
| `--wait` | Wait before repackaging |
| `--verbosity` | Verbosity level (1-3) |

## 🔧 Development

For developers who want to contribute:

```bash
make help    # Show all available commands
make dev     # Setup development environment
make test    # Run tests
make lint    # Check code quality
```

## 🐛 Troubleshooting

**Dependency issues:**
```bash
fridapk --update-gadgets  # Downloads required gadgets
```

**Docker USB access (Linux):**
```bash
sudo usermod -a -G plugdev $USER
sudo chmod 666 /dev/bus/usb/*/*
```

**Device not detected:**
```bash
adb devices  # Check ADB connection
```

## 📝 License

GCU License - see [LICENSE](LICENSE) file for details.

---

**⭐ If FridAPK helps you, please star this repository!**
