import getopt, sys
from os import urandom, getenv
from socket import socket, AF_INET, SOCK_STREAM
from struct import pack
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, padding
from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.hashes import SHA1
from dotenv import load_dotenv

# Constants defitions
SYMMETRIC_KEY_SIZE = 256 // 8
IV_SIZE = 128 // 8

# Function to load a PK pem file 
def load_pem_file(path):
    return serialization.load_pem_public_key(open(path, 'rb').read(), backend=default_backend())

class MixnetClient:

    def __init__(self, entry: str = None, port: int = None) -> None:
        load_dotenv()
        self.entry = entry if entry is not None else getenv('MIXNET_ENTRY')
        self.port = port if port is not None else int(getenv('PORT'))
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect((self.entry, self.port))

    # Function to sends messages to the mixnet
    def send(self, payload: str) -> None:
        payload_size = len(payload)
        packet_format = f'!I{payload_size}s'
        packet = pack(packet_format, payload_size, payload)

        self.socket.send(packet)

    # Function to perform a hybrid encryption of a message using RSA and AES
    def hybrid_encrypt(self, plaintext, public_key):
        # Generate PKSCS#7 padding of size AES block size 
        pkcs7_padder = padding.PKCS7(AES.block_size).padder()

        # Add the padding to the plaintext
        padded_plaintext = pkcs7_padder.update(plaintext) + pkcs7_padder.finalize()

        # Generate a new random AES-256 symmetric key
        key = urandom(SYMMETRIC_KEY_SIZE)

        # Generate a new random 128 IV required for CBC mode
        iv = urandom(IV_SIZE)

        # AES CBC Cipher
        aes_cbc_cipher = Cipher(AES(key), CBC(iv))

        # Encrypt padded plaintext using AES CBC
        ciphertext = aes_cbc_cipher.encryptor().update(padded_plaintext)

        # Generate OAEP padding for RSA encryption
        oaep_padding = asymmetric_padding.OAEP(mgf=asymmetric_padding.MGF1(algorithm=SHA1()), algorithm=SHA1(), label=None)

        # Encrypt iv and symmetric AES key using RSA
        cipherkey = public_key.encrypt(iv + key, oaep_padding)

        # Encrypted message
        return cipherkey + ciphertext

    def encrypt_message(self, message):
        pk_mix_1 = load_pem_file('./public-keys/public-key-mix-1.pem')
        pk_mix_2 = load_pem_file('./public-keys/public-key-mix-2.pem')
        pk_mix_3 = load_pem_file('./public-keys/public-key-mix-3.pem')

        return self.hybrid_encrypt(self.hybrid_encrypt(self.hybrid_encrypt(message, pk_mix_3), pk_mix_2), pk_mix_1)

