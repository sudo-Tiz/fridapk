# FridAPK

> **🔥 Automatically patch Android APKs with Frida Gadget**

FridAPK is a powerful tool that automates the injection of Frida Gadget into Android APKs, enabling dynamic analysis and reverse engineering without root access. It provides a clean, modular architecture with Docker support for easy deployment.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Frida](https://img.shields.io/badge/Frida-Dynamic%20Analysis-red.svg)](https://frida.re/)

## ✨ Features

- 🔄 **Automatic Frida Gadget injection** - No more manual patching
- 📱 **Device architecture detection** - Auto-selects the right gadget  
- 🔐 **User certificate authorities support** - Bypass certificate pinning
- 📜 **Auto-load JavaScript hooks** - Embed scripts directly in APK
- ✍️ **APK signing and alignment** - Production-ready output
- 🐳 **Docker support** - Zero-dependency environment
- 🎯 **Interactive mode** - Step-by-step control
- 🛠️ **Extensible architecture** - Easy to modify and extend

## 🚀 Quick Start

### Option 1: Docker (Recommended)

The easiest way to use FridAPK is with Docker, which includes all dependencies:

```bash
# Clone the repository
git clone https://github.com/sudo-Tiz/fridapk
cd fridapk

# Create workspace directory
mkdir -p workspace

# Copy your APK to the workspace
cp your-app.apk workspace/

# Start the environment (safe mode - no USB access)
docker-compose up -d fridapk-safe

# Run FridAPK
docker-compose exec fridapk-safe fridapk -a /home/fridapk/workspace/your-app.apk
```

#### Docker Usage Examples

```bash
# Update Frida gadgets
docker-compose exec fridapk-safe fridapk --update-gadgets

# Patch APK with device auto-detection (requires USB access)
docker-compose up -d fridapk
docker-compose exec fridapk fridapk -a /home/fridapk/workspace/app.apk

# Enable user certificates
docker-compose exec fridapk-safe fridapk -a /home/fridapk/workspace/app.apk --enable-user-certs

# Auto-load JavaScript hook
docker-compose exec fridapk-safe fridapk -a /home/fridapk/workspace/app.apk --autoload-script /home/fridapk/workspace/hook.js

# Interactive shell
docker-compose exec fridapk-safe bash
```

#### Docker Services

- **`fridapk`**: Full access with USB device support (requires privileged mode)
- **`fridapk-safe`**: Safe mode without USB access (recommended for APK processing only)

### Option 2: Manual Installation

If you prefer to install dependencies manually:

#### Dependencies

**Python packages:**
```bash
pip3 install requests frida frida-tools
```

**System tools** (must be in PATH):
- **apktool** - [Download](https://ibotpeaches.github.io/Apktool/install/)
- **Android SDK tools**: `aapt`, `zipalign`, `adb`, `apksigner`
- **Java tools**: `keytool`, `jarsigner` (from JDK)
- **unxz** - XZ decompression utility

#### Installation

```bash
git clone https://github.com/sudo-Tiz/fridapk
cd fridapk
pip3 install -r requirements.txt

# Make executable
chmod +x fridapk

# Test installation
./fridapk --help
```

## 📖 Usage Guide

### Basic Usage

```bash
# Patch APK with auto-detected Frida gadget
fridapk -a app.apk

# Use specific gadget file
fridapk -a app.apk -g /path/to/frida-gadget.so

# Enable user certificate authorities (for HTTPS interception)
fridapk -a app.apk --enable-user-certs

# Skip Frida gadget injection
fridapk -a app.apk --prevent-gadget
```

### Advanced Features

```bash
# Auto-load JavaScript hook
fridapk -a app.apk --autoload-script hook.js

# Force resource extraction
fridapk -a app.apk --force-resources

# Wait before repackaging (for manual modifications)
fridapk -a app.apk --wait

# Execute custom command before repackaging
fridapk -a app.apk --exec-command "find TMP_PATH_HERE -name '*.so'" --pass-temp-path

# Use aapt2 for building
fridapk -a app.apk --use-aapt2

# Combine multiple options
fridapk -a app.apk --enable-user-certs --autoload-script hook.js --keep-keystore
```

### Frida Gadget Management

```bash
# Update gadgets for current Frida version
fridapk --update-gadgets

# Check available gadgets
ls gadgets/$(frida --version)/
```

## 🛠️ Configuration

### Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--apk` | `-a` | APK file to patch |
| `--output` | `-o` | Output file path |
| `--gadget` | `-g` | Specific gadget file |
| `--autoload-script` | | JavaScript file to auto-load |
| `--update-gadgets` | | Update Frida gadgets |
| `--enable-user-certs` | | Enable user certificate authorities |
| `--prevent-gadget` | | Skip Frida gadget injection |
| `--force-resources` | `-f` | Force resource extraction |
| `--use-aapt2` | | Use aapt2 for building |
| `--keep-keystore` | `-k` | Keep generated keystore |
| `--wait` | `-w` | Wait before repackaging |
| `--exec-command` | `-x` | Execute custom command |
| `--pass-temp-path` | | Pass temp directory to command |
| `--verbosity` | `-v` | Verbosity level (1-3) |

### File Structure

```
fridapk/
├── src/                    # Python source code
│   ├── core/              # Core functionality
│   ├── utils/             # Utilities and helpers
│   └── main.py            # Main application
├── gadgets/               # Downloaded Frida gadgets
├── workspace/             # Working directory (Docker)
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # Docker services
└── fridapk                # Main executable
```

### Environment Variables

- `ANDROID_HOME`: Android SDK location
- `JAVA_HOME`: Java installation path  
- `FRIDA_VERSION`: Override Frida version detection

## 🔧 Architecture

The modular architecture provides better maintainability and extensibility:

- **Modular design**: Separated core functionality, CLI, and utilities
- **Exception handling**: Proper error types and recovery
- **Dependency management**: Smart tool detection and validation
- **Configuration system**: Centralized settings and constants
- **Logging system**: Structured output with verbosity levels

### Core Components

- `DependencyChecker`: Validates and manages system dependencies
- `GadgetManager`: Downloads and manages Frida gadgets
- `APKProcessor`: Handles APK extraction, modification, and repackaging
- `Logger`: Provides consistent, colored output

## 📱 Device Connection

### USB Debugging

For device architecture detection:

1. Enable USB debugging on your Android device
2. Connect device via USB
3. Run FridAPK - it will automatically detect architecture

### ADB over WiFi

```bash
# Connect via WiFi (device and computer on same network)
adb connect <device-ip>:5555
```

## 🎯 Use Cases

### Reverse Engineering

```bash
# Basic Frida gadget injection
fridapk -a target.apk

# With auto-load hook for immediate analysis
fridapk -a target.apk --autoload-script analysis.js
```

### Penetration Testing

```bash
# Enable user certificates for proxy tools
fridapk -a target.apk --enable-user-certs

# Combine with custom modifications
fridapk -a target.apk --enable-user-certs --wait
```

### Development & Testing

```bash
# Patch APK and keep keystore for consistent signing
fridapk -a debug.apk --keep-keystore
```

## 🐛 Troubleshooting

### Common Issues

**"Dependency not found"**
```bash
# Check which tools are missing
fridapk --update-gadgets  # This also checks dependencies
```

**"APK extraction failed"**
```bash
# Try without resource extraction
fridapk -a app.apk --prevent-gadget --force-resources
```

**"Device not detected"**
```bash
# Check ADB connection
adb devices

# Use specific gadget instead
fridapk -a app.apk -g gadgets/16.0.1/frida-gadget-android-arm64.so
```

**Docker USB access issues**
```bash
# Ensure proper permissions (Linux)
sudo usermod -a -G plugdev $USER
sudo chmod 666 /dev/bus/usb/*/*

# Use the privileged service
docker-compose up -d fridapk
```

### Debug Mode

```bash
# Maximum verbosity for debugging
fridapk -a app.apk -v 3
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests, report bugs, or suggest features.

### Development Setup

```bash
git clone https://github.com/sudo-Tiz/fridapk
cd fridapk
pip3 install -r requirements.txt

# Run tests
python -m pytest tests/
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Frida](https://frida.re/) - Dynamic instrumentation toolkit
- [APKTool](https://ibotpeaches.github.io/Apktool/) - APK reverse engineering tool
- Android Security community for inspiration and feedback

## 📚 Related Projects

- [Frida](https://github.com/frida/frida) - Dynamic instrumentation toolkit
- [Objection](https://github.com/sensepost/objection) - Runtime mobile exploration
- [APKTool](https://github.com/iBotPeaches/Apktool) - APK reverse engineering

---

**⭐ If you find FridAPK useful, please star this repository!**

For questions, issues, or feature requests, please open an issue on GitHub.
