from jxdb import JsonDB
from collections import namedtuple
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import ChaCha20_Poly1305
from Crypto.Random import get_random_bytes
import hashlib
import base64
import string
import bcrypt
import random
import os
import sys

Message = namedtuple('Message', ['text', 'attachments'])

CONFIG = {
    'database_path': 'databases/data.jxdb',
    'database_password': "mXxdrZc7uhN8zFDY",
    'hash_algo': hashlib.sha3_256,
    'scripts_path': '.',
    'adduser_script_path': 'adduser.py'
}

sys.path.append(CONFIG['scripts_path'])

while True:
    from utils import SymmetricEncryption as senc
    from mda import MailDeliveryAgent as mda
    break

DB_PATH = CONFIG['database_path']
DB_PASS = CONFIG['database_password']
HASH_ALGO = CONFIG['hash_algo']


def is_mailbox_exists(mail_addr: str):
    db = JsonDB()
    db.open(DB_PATH, DB_PASS)
    if mail_addr in db.keys():
        return True
    else:
        return False


def get_mailbox_publickey(mail_addr: str):
    db = JsonDB()
    db.open(DB_PATH, DB_PASS)
    return db.get(mail_addr+'/pubkey').encode()


def get_mailbox_privkey(mail_addr: str):
    db = JsonDB()
    db.open(DB_PATH, DB_PASS)
    return db.get(mail_addr+'/privkey').encode()


def check_password(mailaddr: str, password: str):
    passhash = HASH_ALGO(password.encode('utf-8')).hexdigest()
    db = JsonDB()
    db.open(DB_PATH, DB_PASS)
    if db.get(mailaddr) == passhash:
        return True
    else:
        return False


def get_mailbox_messages(mail_addr: str):
    db = JsonDB()
    db.open(DB_PATH, DB_PASS)
    parted_messages = db.keyconcept(f'{mail_addr}/message/')
    messages = []
    for msg in parted_messages:
        if msg.count('/') == 2:
            _, __, msg_id = msg.split('/')
            messages.append(msg_id)
    return messages


def create_user(mailbox_addr, password):
    adduser_script_path = CONFIG['adduser_script_path']
    os.system(f'python {adduser_script_path} {mailbox_addr} {password}')


def delete_all_user_data(mailbox_addr):
    db = JsonDB()
    db.open(DB_PATH, DB_PASS)
    db.delete_by_key(mailbox_addr)
    db.save(DB_PATH, DB_PASS)

def delete_message(mail_addr: str, msg_id: str):
    db = JsonDB()
    db.open(DB_PATH, DB_PASS)
    db.delete_by_key(f'{mail_addr}/message/{msg_id}')
    db.save(DB_PATH, DB_PASS)

def message(mail_addr: str, user_password: str, message_id: str):
    db = JsonDB()
    db.open(DB_PATH, DB_PASS)
    encrypted_key = base64.b64decode(
        db.get(f'{mail_addr}/message/{message_id}/key').encode())
    encrypted_text = db.get(f'{mail_addr}/message/{message_id}')
    list_attachments = db.keyconcept(f'{mail_addr}/message/{message_id}/')
    encrypted_private_key = get_mailbox_privkey(mail_addr)
    private_key = RSA.import_key(
        encrypted_private_key, passphrase=user_password)

    cipher = PKCS1_OAEP.new(private_key)

    session_key = cipher.decrypt(encrypted_key).decode()

    text = senc.decrypt(encrypted_text, session_key).decode()
    attachments = []
    if not list_attachments == []:
        for att in list_attachments:
            if not att.endswith('/key'):
                filename = att.split('/')[-1]
                content = senc.decrypt(db.get(att), session_key)
                formated = {
                    'name': filename,
                    'mime_type': 'application/octet-stream',
                    'content': content
                }
                attachments.append(formated)

    return Message(text, attachments)
