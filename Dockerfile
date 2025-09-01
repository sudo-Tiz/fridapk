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

# Create non-root user for security
RUN groupadd -r fridapk && \
    useradd -r -g fridapk -m -s /bin/bash fridapk && \
    mkdir -p /home/fridapk/workspace && \
    chown -R fridapk:fridapk /home/fridapk

# Copy FridAPK source code
COPY --chown=fridapk:fridapk . /fridapk/

# Make scripts executable
RUN chmod +x /fridapk/apkpatcher_new && \
    chmod +x /fridapk/apkpatcher

# Switch to non-root user
USER fridapk

# Create gadgets directory
RUN mkdir -p /home/fridapk/.fridapk/gadgets

# Set environment variables for FridAPK
ENV FRIDAPK_HOME=/home/fridapk/.fridapk
ENV PATH=/fridapk:${PATH}

# Expose ADB port (for device connection)
EXPOSE 5037

# Set default working directory for user
WORKDIR /home/fridapk/workspace

# Health check to verify all tools are working
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import frida; print('Frida:', frida.__version__)" && \
        apktool --version && \
        aapt version && \
        echo "FridAPK Docker environment is healthy"

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
