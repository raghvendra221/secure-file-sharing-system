import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from django.conf import settings

# Use 32 bytes key (AES-256)
MASTER_KEY = settings.SECRET_KEY[:32].encode()


def encrypt_with_key(data,key):
    iv = os.urandom(16)

    cipher = Cipher(
        algorithms.AES(key),
        modes.CFB(iv),
        backend=default_backend()
    )

    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data) + encryptor.finalize()

    return iv + encrypted_data


def decrypt_with_key(encrypted_data,key):
    iv = encrypted_data[:16]
    actual_data = encrypted_data[16:]

    cipher = Cipher(
        algorithms.AES(key),
        modes.CFB(iv),
        backend=default_backend()
    )

    decryptor = cipher.decryptor()
    return decryptor.update(actual_data) + decryptor.finalize()

def generate_file_key():
    return os.urandom(32)


