#!/usr/bin/env python3
"""
FridAPK - APK processing utilities
"""

import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional

from config import Config
from exceptions import APKError, ExtractionError, RepackageError, SigningError
from utils.logger import Logger


class APKProcessor:
    """Handles APK extraction, modification, and repackaging"""

    def __init__(self, logger: Logger, config: Config):
        self.logger = logger
        self.config = config

    def create_temp_folder(self, apk_path: Path) -> Path:
        """Create temporary folder for APK processing"""
        apk_name = apk_path.stem.replace(".", "_")
        temp_dir = self.config.temp_dir / apk_name

        if temp_dir.exists():
            self.logger.info("Temp directory exists. Removing...")
            shutil.rmtree(temp_dir)

        temp_dir.mkdir(parents=True)
        self.logger.info(f"Created temp directory: {temp_dir}")

        return temp_dir

    def extract_apk(
        self, apk_path: Path, destination: Path, extract_resources: bool = True
    ) -> None:
        """Extract APK using apktool"""
        try:
            cmd = ["apktool", "-f"]

            if not extract_resources:
                cmd.append("-r")
                self.logger.info(
                    f"Extracting {apk_path.name} (without resources) to {destination}"
                )
            else:
                self.logger.info(
                    f"Extracting {apk_path.name} (with resources) to {destination}"
                )
                self.logger.info("Some errors may occur while decoding resources")

            cmd.extend(["d", "-o", str(destination), str(apk_path)])

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            if result.stderr:
                self.logger.debug(f"apktool stderr: {result.stderr}")

        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to extract APK: {e.stderr if e.stderr else str(e)}"
            raise ExtractionError(error_msg)

    def repackage_apk(
        self, source_dir: Path, output_path: Path, use_aapt2: bool = False
    ) -> Path:
        """Repackage APK using apktool"""
        # Generate unique filename if file exists
        if output_path.exists():
            timestamp = str(time.time()).replace(".", "")
            output_path = output_path.with_stem(f"{output_path.stem}_{timestamp}")

        self.logger.info(f"Repackaging APK to {output_path}")
        self.logger.info("This may take some time...")

        try:
            cmd = ["apktool"]

            if use_aapt2:
                cmd.append("--use-aapt2")

            cmd.extend(["b", "-o", str(output_path), str(source_dir)])

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            if result.stderr:
                self.logger.debug(f"apktool stderr: {result.stderr}")

            self.logger.success("APK repackaged successfully")
            return output_path

        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to repackage APK: {e.stderr if e.stderr else str(e)}"
            raise RepackageError(error_msg)

    def sign_and_align_apk(self, apk_path: Path, keep_keystore: bool = False) -> None:
        """Sign and align APK"""
        try:
            keystore_path = Path("fridapkkeystore")

            # Generate keystore if needed
            if not keystore_path.exists():
                self._generate_keystore(keystore_path)

            # Sign with v1 signature
            self._sign_v1(apk_path, keystore_path)

            # Align APK
            self._align_apk(apk_path)

            # Sign with v2 signature
            self._sign_v2(apk_path, keystore_path)

            # Clean up keystore if requested
            if not keep_keystore and keystore_path.exists():
                keystore_path.unlink()

            self.logger.success("APK signed and aligned successfully")

        except Exception as e:
            raise SigningError(f"Failed to sign APK: {str(e)}")

    def _generate_keystore(self, keystore_path: Path) -> None:
        """Generate a keystore for signing"""
        self.logger.info("Generating signing key...")

        cmd = [
            "keytool",
            "-genkey",
            "-keyalg",
            "RSA",
            "-keysize",
            "2048",
            "-validity",
            "700",
            "-noprompt",
            "-alias",
            "fridapkalias1",
            "-dname",
            "CN=fridapk.com, OU=ID, O=FridAPK, L=Frida, S=APK, C=BR",
            "-keystore",
            str(keystore_path),
            "-storepass",
            "password",
            "-keypass",
            "password",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise SigningError(f"Failed to generate keystore: {result.stderr}")

    def _sign_v1(self, apk_path: Path, keystore_path: Path) -> None:
        """Sign APK with v1 signature (jarsigner)"""
        self.logger.info("Signing APK with v1 signature...")

        cmd = [
            "jarsigner",
            "-sigalg",
            "SHA1withRSA",
            "-digestalg",
            "SHA1",
            "-keystore",
            str(keystore_path),
            "-storepass",
            "password",
            str(apk_path),
            "fridapkalias1",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise SigningError(f"Failed to sign with jarsigner: {result.stderr}")

    def _align_apk(self, apk_path: Path) -> None:
        """Align APK with zipalign"""
        self.logger.info("Aligning APK with zipalign...")

        temp_path = apk_path.with_suffix(".tmp.apk")
        apk_path.rename(temp_path)

        cmd = ["zipalign", "-p", "-f", "4", str(temp_path), str(apk_path)]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            # Restore original file
            temp_path.rename(apk_path)
            raise SigningError(f"Failed to align APK: {result.stderr}")

        temp_path.unlink()

    def _sign_v2(self, apk_path: Path, keystore_path: Path) -> None:
        """Sign APK with v2 signature (apksigner)"""
        self.logger.info("Signing APK with v2 signature...")

        cmd = [
            "apksigner",
            "sign",
            "--ks-key-alias",
            "fridapkalias1",
            "--ks",
            str(keystore_path),
            "--ks-pass",
            "pass:password",
            str(apk_path),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            self.logger.warning(f"v2 signing failed: {result.stderr}")
            # v2 signing is optional, so we don't raise an error

    def has_permission(self, apk_path: Path, permission: str) -> bool:
        """Check if APK has specific permission"""
        try:
            result = subprocess.run(
                ["aapt", "dump", "permissions", str(apk_path)],
                capture_output=True,
                text=True,
                check=True,
            )

            has_perm = permission in result.stdout

            if has_perm:
                self.logger.info(f'APK has permission "{permission}"')
            else:
                self.logger.info(f'APK does not have permission "{permission}"')

            return has_perm

        except subprocess.CalledProcessError as e:
            raise APKError(f"Failed to check permissions: {e}")

    def get_main_activity(self, apk_path: Path) -> Optional[str]:
        """Get main activity class name from APK"""
        try:
            result = subprocess.run(
                ["aapt", "dump", "badging", str(apk_path)],
                capture_output=True,
                text=True,
                check=True,
            )

            for line in result.stdout.split("\n"):
                if "launchable-activity:" in line:
                    # Extract activity name
                    name_start = line.find("name=")
                    if name_start != -1:
                        name_part = line[name_start:].split()[0]
                        activity_name = name_part.replace("name=", "").strip("'\"")

                        self.logger.info(f"Found main activity: {activity_name}")
                        return activity_name

            self.logger.warning("No main activity found")
            return None

        except subprocess.CalledProcessError as e:
            raise APKError(f"Failed to get main activity: {e}")
