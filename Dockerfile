# FridAPK Docker Environment
# Based on Ubuntu 22.04 LTS with all required dependencies

FROM ubuntu:22.04

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Paris

# Set working directory
WORKDIR /fridapk

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Basic tools
    curl \
    wget \
    unzip \
    xz-utils \
    git \
    # Python and pip
    python3 \
    python3-pip \
    python3-venv \
    # Java (required for Android tools)
    openjdk-11-jdk \
    # Build tools
    build-essential \
    # ADB and Android tools dependencies
    libc6-dev-i386 \
    lib32z1 \
    lib32stdc++6 \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=${JAVA_HOME}/bin:${PATH}

# Install Python dependencies
RUN pip3 install --no-cache-dir \
    frida \
    frida-tools \
    requests

# Create Android SDK directory
ENV ANDROID_HOME=/opt/android-sdk
ENV ANDROID_SDK_ROOT=${ANDROID_HOME}
RUN mkdir -p ${ANDROID_HOME}

# Download and install Android SDK Command Line Tools
RUN cd /tmp && \
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip && \
    unzip -q commandlinetools-linux-9477386_latest.zip && \
    mkdir -p ${ANDROID_HOME}/cmdline-tools && \
    mv cmdline-tools ${ANDROID_HOME}/cmdline-tools/latest && \
    rm commandlinetools-linux-9477386_latest.zip

# Add Android tools to PATH
ENV PATH=${ANDROID_HOME}/cmdline-tools/latest/bin:${ANDROID_HOME}/platform-tools:${ANDROID_HOME}/build-tools/33.0.2:${PATH}

# Install Android SDK components
RUN yes | sdkmanager --licenses && \
    sdkmanager "platform-tools" "build-tools;33.0.2" "platforms;android-33"

# Download and install APKTool
RUN cd /tmp && \
    wget -q https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool -O apktool && \
    wget -q https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.8.1.jar -O apktool.jar && \
    chmod +x apktool && \
    mv apktool /usr/local/bin/ && \
    mv apktool.jar /usr/local/bin/

# Create symbolic links for Android tools (for compatibility)
RUN ln -sf ${ANDROID_HOME}/build-tools/33.0.2/aapt /usr/local/bin/aapt && \
    ln -sf ${ANDROID_HOME}/build-tools/33.0.2/zipalign /usr/local/bin/zipalign && \
    ln -sf ${ANDROID_HOME}/build-tools/33.0.2/apksigner /usr/local/bin/apksigner && \
    ln -sf ${ANDROID_HOME}/platform-tools/adb /usr/local/bin/adb

# Download and install Frida gadgets directly to final location
RUN set -e && \
    echo "Downloading Frida gadgets..." && \
    mkdir -p /fridapk/gadgets && \
    VERSION=$(curl -s https://api.github.com/repos/frida/frida/releases/latest | grep '"tag_name":' | cut -d'"' -f4) && \
    echo "Latest Frida version: $VERSION" && \
    for ARCH in android-arm android-arm64 android-x86 android-x86_64; do \
        echo "Downloading gadget for $ARCH..." && \
        wget -q "https://github.com/frida/frida/releases/download/$VERSION/frida-gadget-$VERSION-$ARCH.so.xz" -O "/tmp/gadget.xz" && \
        unxz -c "/tmp/gadget.xz" > "/fridapk/gadgets/frida-gadget-$ARCH.so" && \
        rm "/tmp/gadget.xz" && \
        echo "Extracted: frida-gadget-$ARCH.so"; \
    done && \
    echo "All Frida gadgets downloaded successfully"

# Create non-root user for security
RUN groupadd -r fridapk && \
    useradd -r -g fridapk -s /bin/bash fridapk

# Copy FridAPK source code
COPY . /fridapk/

# Set permissions and make executable
RUN chown -R fridapk:fridapk /fridapk && \
    chmod +x /fridapk/fridapk

# Switch to non-root user
USER fridapk

# Set environment variables for FridAPK
ENV FRIDAPK_GADGETS_DIR=/fridapk/gadgets
ENV FRIDAPK_TEMP_DIR=/tmp/fridapk
ENV PATH=/fridapk:${PATH}
ENV PYTHONPATH=/fridapk/src

# Expose ADB port (for device connection)
EXPOSE 5037

# Default command
CMD ["/bin/bash"]

# Labels for metadata
LABEL maintainer="sudo-Tiz <https://github.com/sudo-Tiz>" \
      version="2.0" \
      description="FridAPK Docker environment with all dependencies" \
      org.opencontainers.image.title="FridAPK" \
      org.opencontainers.image.description="Docker environment for APK patching with Frida Gadget" \
      org.opencontainers.image.url="https://github.com/sudo-Tiz/fridapk" \
      org.opencontainers.image.source="https://github.com/sudo-Tiz/fridapk" \
      org.opencontainers.image.version="2.0" \
      org.opencontainers.image.created="2025-09-01"
