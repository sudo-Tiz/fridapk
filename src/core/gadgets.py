#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FridAPK - Frida Gadget Manager
"""

import requests
import subprocess
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

from config import Architecture, URLs, Config
from exceptions import GadgetError, DependencyError
from utils.logger import Logger


@dataclass
class GadgetInfo:
    """Information about a Frida gadget"""
    name: str
    url: str
    arch: str
    version: str
    local_path: Optional[Path] = None


class GadgetManager:
    """Manages Frida gadgets download and selection"""
    
    def __init__(self, logger: Logger, config: Config):
        self.logger = logger
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FridAPK/1.0'
        })
    
    def get_frida_version(self) -> str:
        """Get installed Frida version"""
        try:
            result = subprocess.run(
                ['frida', '--version'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            raise DependencyError(f"Frida not found or not working: {e}")
    
    def download_gadgets_for_version(self, version: str) -> List[GadgetInfo]:
        """Download all gadgets for a specific Frida version"""
        self.logger.info(f'Downloading gadgets for Frida version: {version}')
        
        # Get release information
        gadgets = self._get_gadgets_for_version(version)
        
        if not gadgets:
            raise GadgetError(f"No gadgets found for Frida version {version}")
        
        # Create version directory
        version_dir = self.config.gadgets_dir / version
        version_dir.mkdir(parents=True, exist_ok=True)
        
        # Download gadgets
        downloaded = []
        for gadget in gadgets:
            local_file = version_dir / gadget.name
            
            # Skip if already exists (uncompressed version)
            if local_file.with_suffix('').exists():
                self.logger.info(f'{gadget.name} already exists. Skipping.')
                gadget.local_path = local_file.with_suffix('')
                downloaded.append(gadget)
                continue
            
            # Download
            self._download_file(gadget.url, local_file)
            
            # Extract if compressed
            if local_file.suffix == '.xz':
                self._extract_xz(local_file)
                gadget.local_path = local_file.with_suffix('')
            else:
                gadget.local_path = local_file
            
            downloaded.append(gadget)
        
        self.logger.success(f'Downloaded {len(downloaded)} gadgets')
        return downloaded
    
    def _get_gadgets_for_version(self, version: str) -> List[GadgetInfo]:
        """Get gadget download URLs for a specific version"""
        try:
            # Get releases list
            response = self.session.get(URLs.FRIDA_RELEASES, timeout=30)
            response.raise_for_status()
            releases = response.json()
            
            # Find the specific version
            target_release = None
            for release in releases:
                if release['tag_name'] == version:
                    target_release = release
                    break
            
            if not target_release:
                raise GadgetError(f"Version {version} not found in releases")
            
            # Get release details
            response = self.session.get(target_release['url'], timeout=30)
            response.raise_for_status()
            release_data = response.json()
            
            # Extract gadget assets
            gadgets = []
            for asset in release_data.get('assets', []):
                name = asset['name']
                if 'gadget' in name.lower() and 'android' in name.lower():
                    arch = self._detect_architecture_from_filename(name)
                    gadgets.append(GadgetInfo(
                        name=name,
                        url=asset['browser_download_url'],
                        arch=arch,
                        version=version
                    ))
            
            return gadgets
            
        except requests.RequestException as e:
            raise GadgetError(f"Failed to fetch release information: {e}")
        except KeyError as e:
            raise GadgetError(f"Unexpected API response format: {e}")
    
    def _detect_architecture_from_filename(self, filename: str) -> str:
        """Detect architecture from gadget filename"""
        filename = filename.lower()
        
        if 'arm64' in filename:
            return Architecture.ARM64
        elif 'arm' in filename:
            return Architecture.ARM
        elif 'x86_64' in filename:
            return Architecture.X64
        elif 'i386' in filename or 'x86' in filename:
            return Architecture.X86
        
        return 'unknown'
    
    def _download_file(self, url: str, target_path: Path) -> None:
        """Download a file with progress indication"""
        try:
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(target_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = int(downloaded * 100 / total_size)
                            self.logger.info(f'Downloading {target_path.name} - {progress:03d}%')
            
            self.logger.success(f'Downloaded {target_path.name}')
            
        except requests.RequestException as e:
            raise GadgetError(f"Failed to download {url}: {e}")
    
    def _extract_xz(self, compressed_file: Path) -> None:
        """Extract XZ compressed file"""
        try:
            subprocess.run(['unxz', str(compressed_file)], check=True)
            self.logger.info(f'Extracted {compressed_file.name}')
        except subprocess.SubprocessError as e:
            raise GadgetError(f"Failed to extract {compressed_file}: {e}")
    
    def get_device_architecture(self) -> str:
        """Get connected device architecture via ADB"""
        try:
            self.logger.info('Waiting for device...')
            subprocess.run(['adb', 'wait-for-device'], check=True, timeout=30)
            
            result = subprocess.run(
                ['adb', 'shell', 'getprop', 'ro.product.cpu.abi'],
                capture_output=True,
                text=True,
                check=True
            )
            
            abi = result.stdout.strip()
            self.logger.info(f'Device ABI: {abi}')
            
            # Map ABI to our architecture constants
            arch_mapping = {
                'armeabi': Architecture.ARM,
                'armeabi-v7a': Architecture.ARM,
                'arm64-v8a': Architecture.ARM64,
                'x86': Architecture.X86,
                'x86_64': Architecture.X64,
            }
            
            return arch_mapping.get(abi, abi)
            
        except subprocess.SubprocessError as e:
            raise GadgetError(f"Failed to get device architecture: {e}")
    
    def find_gadget_for_architecture(self, arch: str, version: str = None) -> Optional[Path]:
        """Find appropriate gadget for given architecture"""
        if version is None:
            version = self.get_frida_version()
        
        version_dir = self.config.gadgets_dir / version
        
        if not version_dir.exists():
            self.logger.warning(f'Gadget folder not found for version {version}. Try updating gadgets.')
            return None
        
        # Search for gadgets matching the architecture
        for gadget_file in version_dir.iterdir():
            if not gadget_file.is_file():
                continue
            
            filename = gadget_file.name.lower()
            if 'gadget' not in filename:
                continue
            
            gadget_arch = self._detect_architecture_from_filename(filename)
            if gadget_arch == arch:
                self.logger.info(f'Found gadget for {arch}: {gadget_file.name}')
                return gadget_file
        
        self.logger.warning(f'No gadget found for architecture: {arch}')
        return None
    
    def get_recommended_gadget(self) -> Optional[Path]:
        """Get recommended gadget for connected device"""
        try:
            device_arch = self.get_device_architecture()
            return self.find_gadget_for_architecture(device_arch)
        except GadgetError as e:
            self.logger.warning(f"Could not get recommended gadget: {e}")
            return None
    
    def update_gadgets(self) -> bool:
        """Update gadgets for current Frida version"""
        try:
            version = self.get_frida_version()
            self.download_gadgets_for_version(version)
            return True
        except (GadgetError, DependencyError) as e:
            self.logger.error(f"Failed to update gadgets: {e}")
            return False
