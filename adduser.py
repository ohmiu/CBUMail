import argparse
import re
import logging
import os
import hashlib
from jxdb import JsonDB
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from config import CONFIG

DB_PASS = CONFIG['database_password']
DB_PATH = CONFIG['database_path']

if CONFIG['hash_algo'] == 'sha3-256':
    HASH_ALGO = hashlib.sha3_256
elif CONFIG['hash_algo'] == 'sha256':
    HASH_ALGO = hashlib.sha256
elif CONFIG['hash_algo'] == 'md5':
    HASH_ALGO = hashlib.md5
elif CONFIG['hash_algo'] == 'sha1':
    HASH_ALGO = hashlib.sha1
elif CONFIG['hash_algo'] == 'sha224':
    HASH_ALGO = hashlib.sha224
else:
    logging.critical('Unknown hash algo - change it in config.py')
    os._exit(1)


def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email)


def add_user(email, password):
    if not os.path.exists(DB_PATH):
        def create_db():
            db = JsonDB()
            db.save(DB_PATH, DB_PASS)
        create_db()
    try:
        db = JsonDB()
        print('Generating key pair (RSA 4096)...')
        private_key = RSA.generate(4096)
        public_key = private_key.publickey()
        privkey = private_key.export_key(
            passphrase=password, pkcs=8, protection="scryptAndAES128-CBC").decode()
        pubkey = public_key.export_key().decode()
        db.open(DB_PATH, DB_PASS)
        passhash = HASH_ALGO(password.encode('utf-8')).hexdigest()
        print(passhash)
        db.set(email, passhash)
        print('Userdatata saved')
        db.set(email+'/privkey', privkey)
        print('Private key saved')
        db.set(email+'/pubkey', pubkey)
        print('Public key saved')
        db.save(DB_PATH, DB_PASS)
        print(f"[+] - User successfully added: {email}")
    except Exception as err:
        print(str(err))


def base():
    parser = argparse.ArgumentParser(
        description='New user creation')
    parser.add_argument('email', type=str,
                        help='User email (e.g. example@example.com)')
    parser.add_argument('password', type=str,
                        help='User password')

    args = parser.parse_args()

    if not is_valid_email(args.email):
        print("Invalid e-mail address format.")
        return

    add_user(args.email, args.password)


if __name__ == "__main__":
    base()
