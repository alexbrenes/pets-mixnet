from os import urandom
from socket import socket, AF_INET, SOCK_STREAM
from struct import pack
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, padding
from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.hashes import SHA1

# Constants defitions
SYMMETRIC_KEY_SIZE = 256 // 8
IV_SIZE = 128 // 8


class MixnetClient:

    def __init__(self, entry: str, port: int) -> None:
        self.entry = entry
        self.port = port

        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect((entry, port))
        self.pk_mix_1 = self._load_pem_file('./public-key-mix-1.pem')
        self.pk_mix_2 = self._load_pem_file('./public-key-mix-2.pem')
        self.pk_mix_3 = self._load_pem_file('./public-key-mix-3.pem')

    # Function to load a PK pem file
    def _load_pem_file(self, path):
        return serialization.load_pem_public_key(open(path, 'rb').read(), backend=default_backend())

    # Function to send messages to the mixnet
    def send(self, m: str) -> None:
        m_encoded = m.encode()
        encrypted_message = self._protocol_encrypt(m_encoded)
        self._send(encrypted_message)

    def _send(self, payload: bytes):
        payload_size = len(payload)
        packet_format = f'!I{payload_size}s'
        packet = pack(packet_format, payload_size, payload)

        self.socket.send(packet)

    def _protocol_encrypt(self, m: bytes) -> bytes:
        encrypted_message_1 = self.hybrid_encrypt(m, self.pk_mix_3)
        encrypted_message_2 = self.hybrid_encrypt(
            encrypted_message_1, self.pk_mix_2)
        encrypted_message_3 = self.hybrid_encrypt(
            encrypted_message_2, self.pk_mix_1)
        return encrypted_message_3

    # Function to perform a hybrid encryption of a message using RSA and AES
    def hybrid_encrypt(self, plaintext, public_key):
        # Generate PKSCS#7 padding of size AES block size
        pkcs7_padder = padding.PKCS7(AES.block_size).padder()

        # Add the padding to the plaintext
        padded_plaintext = pkcs7_padder.update(
            plaintext) + pkcs7_padder.finalize()

        # Generate a new random AES-256 symmetric key
        key = urandom(SYMMETRIC_KEY_SIZE)

        # Generate a new random 128 IV required for CBC mode
        iv = urandom(IV_SIZE)

        # AES CBC Cipher
        aes_cbc_cipher = Cipher(AES(key), CBC(iv))

        # Encrypt padded plaintext using AES CBC
        ciphertext = aes_cbc_cipher.encryptor().update(padded_plaintext)

        # Generate OAEP padding for RSA encryption
        oaep_padding = asymmetric_padding.OAEP(mgf=asymmetric_padding.MGF1(
            algorithm=SHA1()), algorithm=SHA1(), label=None)

        # Encrypt iv and symmetric AES key using RSA
        cipherkey = public_key.encrypt(iv + key, oaep_padding)

        # Encrypted message
        return cipherkey + ciphertext
    
    def protocol_encrypt(self, m: str) -> bytes:
        m_encoded = m.encode()
        encrypted_message = self._protocol_encrypt(m_encoded)
        return encrypted_message

