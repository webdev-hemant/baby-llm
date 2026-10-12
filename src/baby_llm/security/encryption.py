"""AES-GCM-256 Attribute-Level Encryption backed by the OS Keyring."""

import base64
import logging
import os
from pathlib import Path
from typing import Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import keyring
from baby_llm.config import settings

logger = logging.getLogger(__name__)

KEYRING_SERVICE_NAME = "baby_llm"
KEYRING_USERNAME = "ymyl_master_key"
ENC_PREFIX = "ENC::"


class YMYLEncryptionManager:
    """
    Manages AES-GCM-256 attribute-level encryption for sensitive YMYL
    (Your Money or Your Life: financial, medical) personal facts.
    Backing master key is securely stored in the OS Keyring,
    with an air-gapped local keyfile fallback (~/.baby_llm/.ymyl_key)
    with strict 0600 file permissions.
    """

    def __init__(self, key_path: Optional[Path] = None):
        self.key_path = key_path or (settings.app_dir / ".ymyl_key")
        self._key: Optional[bytes] = None

    def _get_or_create_key(self) -> bytes:
        if self._key is not None:
            return self._key

        # 1. Attempt retrieval from OS Keyring
        try:
            stored_hex = keyring.get_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME)
            if stored_hex and len(stored_hex) == 64:
                self._key = bytes.fromhex(stored_hex)
                return self._key
        except Exception as e:
            logger.debug(f"OS Keyring retrieval failed or unavailable: {e}")

        # 2. Check fallback key file
        if self.key_path.exists():
            try:
                hex_content = self.key_path.read_text(encoding="utf-8").strip()
                if len(hex_content) == 64:
                    self._key = bytes.fromhex(hex_content)
                    return self._key
            except Exception as e:
                logger.warning(f"Failed to read local fallback key file: {e}")

        # 3. Generate new 256-bit (32 bytes) master key
        new_key = AESGCM.generate_key(bit_length=256)
        key_hex = new_key.hex()

        # Try to persist in OS Keyring
        stored_in_keyring = False
        try:
            keyring.set_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME, key_hex)
            stored_in_keyring = True
            logger.info("Successfully provisioned new YMYL master key in OS Keyring.")
        except Exception as e:
            logger.warning(f"Could not store key in OS Keyring: {e}. Falling back to file.")

        # Persist to local secure keyfile with 0600 permissions
        try:
            self.key_path.parent.mkdir(parents=True, exist_ok=True)
            self.key_path.write_text(key_hex, encoding="utf-8")
            try:
                os.chmod(self.key_path, 0o600)
            except Exception:
                pass
            logger.info(f"Provisioned YMYL fallback keyfile at {self.key_path} (mode 0600).")
        except Exception as e:
            if not stored_in_keyring:
                raise RuntimeError(f"Failed to persist YMYL encryption key to keyring or disk: {e}")

        self._key = new_key
        return self._key

    def is_encrypted(self, value: str) -> bool:
        """Determines if a string contains an encrypted ciphertext."""
        return isinstance(value, str) and value.startswith(ENC_PREFIX)

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypts plaintext string with AES-GCM-256.
        Returns: ENC::<base64(12-byte-nonce + ciphertext + 16-byte-tag)>
        """
        if not plaintext:
            return plaintext
        if self.is_encrypted(plaintext):
            return plaintext

        key = self._get_or_create_key()
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)  # 96-bit standard GCM nonce
        raw_ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
        payload = nonce + raw_ciphertext
        encoded = base64.b64encode(payload).decode("utf-8")
        return f"{ENC_PREFIX}{encoded}"

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypts an ENC:: prefixed ciphertext back to plaintext string.
        If plaintext or unencrypted, returns as-is.
        """
        if not self.is_encrypted(ciphertext):
            return ciphertext

        encoded = ciphertext[len(ENC_PREFIX):]
        try:
            payload = base64.b64decode(encoded.encode("utf-8"))
            if len(payload) < 28:  # 12 nonce + 16 tag minimum
                raise ValueError("Payload too short for AES-GCM ciphertext")

            nonce = payload[:12]
            actual_ciphertext = payload[12:]

            key = self._get_or_create_key()
            aesgcm = AESGCM(key)
            decrypted_bytes = aesgcm.decrypt(nonce, actual_ciphertext, None)
            return decrypted_bytes.decode("utf-8")
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError(f"Failed to decrypt YMYL ciphertext: {e}")


ymyl_encryption = YMYLEncryptionManager()
