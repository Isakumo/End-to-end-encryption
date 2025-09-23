import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

# Generate RSA keypair
def generate_keypair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    return public_key, private_key

# Encapsulate a random AES key using RSA public key
def encapsulate_key(public_key):
    # Generate random 32-byte symmetric key
    shared_secret = os.urandom(32)
    ciphertext_key = public_key.encrypt(
        shared_secret,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext_key, shared_secret

# Decapsulate RSA-encrypted symmetric key
def decapsulate_key(private_key, ciphertext_key):
    shared_secret = private_key.decrypt(
        ciphertext_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return shared_secret
