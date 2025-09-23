import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class AESGCMCipher:
    def __init__(self, key: bytes):
        self.key = key

    def encrypt(self, plaintext: bytes, aad: bytes = None) -> (bytes, bytes):
        aesgcm = AESGCM(self.key)
        nonce = os.urandom(12)  # 96-bit nonce
        ciphertext = aesgcm.encrypt(nonce, plaintext, aad)
        return nonce, ciphertext

    def decrypt(self, nonce: bytes, ciphertext: bytes, aad: bytes = None) -> bytes:
        aesgcm = AESGCM(self.key)
        return aesgcm.decrypt(nonce, ciphertext, aad)

    # 🔹 New: encrypt a file
    def encrypt_file(self, input_path: str, output_path: str, aad: bytes = None):
        with open(input_path, "rb") as f:
            data = f.read()
        nonce, ciphertext = self.encrypt(data, aad)
        with open(output_path, "wb") as f:
            f.write(nonce + ciphertext)

    # 🔹 New: decrypt a file
    def decrypt_file(self, input_path: str, output_path: str, aad: bytes = None):
        with open(input_path, "rb") as f:
            filedata = f.read()
        nonce, ciphertext = filedata[:12], filedata[12:]
        plaintext = self.decrypt(nonce, ciphertext, aad)
        with open(output_path, "wb") as f:
            f.write(plaintext)
