import bcrypt
from Crypto.Cipher import ChaCha20_Poly1305
from Crypto.Random import get_random_bytes
import base64
import string
import random

class SymmetricEncryption:

    @staticmethod
    def generate_key_from_password(password, salt):
        key = bcrypt.kdf(password=password.encode('utf-8'), salt=salt, desired_key_bytes=32, rounds=100)
        return key

    @staticmethod
    def encrypt(plaintext, password):
        salt = get_random_bytes(16)
        key = SymmetricEncryption.generate_key_from_password(password, salt)
        nonce = get_random_bytes(24)
        cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))
        return base64.b64encode(salt + nonce + ciphertext + tag).decode('utf-8')

    @staticmethod
    def encrypt_bytes(data, password):
        salt = get_random_bytes(16)
        key = SymmetricEncryption.generate_key_from_password(password, salt)
        nonce = get_random_bytes(24)
        cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        return base64.b64encode(salt + nonce + ciphertext + tag).decode('utf-8')

    @staticmethod
    def decrypt(ciphertext_base64, password):
        ciphertext = base64.b64decode(ciphertext_base64.encode('utf-8'))
        salt = ciphertext[:16]
        nonce = ciphertext[16:40]
        ciphertext_part = ciphertext[40:-16]
        tag = ciphertext[-16:]
        key = SymmetricEncryption.generate_key_from_password(password, salt)
        cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
        try:
            plaintext = cipher.decrypt_and_verify(ciphertext_part, tag)
            return plaintext
        except ValueError:
            print("Decryption or data integrity verification error.")
            return None

class Generator:
    def randomkey(length=29):
        characters = string.ascii_letters + string.digits + "+-/"
        return 'SK-' + ''.join(random.choice(characters) for _ in range(length))