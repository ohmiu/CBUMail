import aiosmtpd.controller
import ssl
import os
import time
import base64
import hashlib
import banner
import logging
import binascii
from colorama import Fore
from datetime import datetime
from email import message_from_string
from config import CONFIG
from jxdb import JsonDB
from threading import Thread
from uuid import uuid4
from mda import MailDeliveryAgent as mdasend
from utils import Generator as generator
from utils import SymmetricEncryption as senc
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

AUTHED_SESSIONS = []
DB_PASS = CONFIG['database_password']
DB_PATH = CONFIG['database_path']
CPORT = CONFIG['port']

if CONFIG['logging_level'] == 'all':
    LOGLVL = logging.INFO
else:
    LOGLVL = logging.WARNING

logging.basicConfig(level=LOGLVL,
                    format='[' + Fore.GREEN + '%(asctime)s' + Fore.RESET + '] - [%(levelname)s] - %(message)s')

if not os.path.exists(DB_PATH):
    def create_db():
        db = JsonDB()
        db.save(DB_PATH, DB_PASS)
    create_db()

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


def add_padding(s):
    padding = b'=' * (len(s) % 4)
    return s + padding


def session_timer(mailaddr: str):
    time.sleep(CONFIG['session_activity_time'])
    AUTHED_SESSIONS.remove(mailaddr)


def check_password(mailaddr: str, hash: str):
    db = JsonDB()
    db.open(DB_PATH, DB_PASS)
    if db.get(mailaddr) == hash:
        return True
    else:
        return False


def is_user_mail_address_exists(mail_addr: str):
    db = JsonDB()
    db.open(DB_PATH, DB_PASS)
    if mail_addr in db.keys():
        return True
    else:
        return False


def get_user_public_key(mail_addr: str):
    db = JsonDB()
    db.open(DB_PATH, DB_PASS)
    return db.get(mail_addr+'/pubkey').encode()


def save_message(from_addr, to_addr, subject, message, attachments, message_id, message_key):
    db = JsonDB()
    db.open(DB_PATH, DB_PASS)

    public_key = RSA.import_key(get_user_public_key(to_addr))
    cipher = PKCS1_OAEP.new(public_key)

    date_today = datetime.now().date()
    time_now = datetime.now().time()
    encrypted_key = base64.b64encode(
        cipher.encrypt(message_key.encode())).decode()

    db.set(f'{to_addr}/message/{message_id}/key', encrypted_key)  # DB key save

    message_formated = f"""Message recieved
Subject: {subject}
From: {from_addr}
To: {to_addr}
At {time_now}, {date_today}

{message}"""

    message_encrypted = senc.encrypt(message_formated, message_key)

    db.set(f'{to_addr}/message/{message_id}',
           message_encrypted)  # DB message save

    for attachment in attachments:
        attachment_name = attachment['name']
        attachment_content = attachment['content']
        encrypted_content = senc.encrypt_bytes(attachment_content, message_key)
        db.set(f'{to_addr}/message/{message_id}/{attachment_name}',
               encrypted_content)

    db.save(DB_PATH, DB_PASS)


context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(CONFIG['tls_cert_path'], CONFIG['tls_key_path'])


class CustomAuthHandler:
    async def auth_PLAIN(server, args):
        try:
            ldata = base64.b64decode(args[1].encode())
            ldata = ldata.split(b'\x00')
            login = ldata[1].decode()

            if login in AUTHED_SESSIONS:
                return f'454 Previous session not yet finished, please wait 30 seconds'

            password = ldata[2].decode().replace('\n', '').replace(' ', '')
            passhash = HASH_ALGO(password.encode()).hexdigest()
            if check_password(login, passhash):
                AUTHED_SESSIONS.append(login)
                Thread(target=session_timer, args=(login, )).start()
                return '235 Authorized successfully'

            else:
                return '535 Incorrect auth data'
        except Exception as e:
            logging.error(str(e))
            return '500 Internal Server Error or data format is invalid'


class Handler:

    async def handle_AUTH(server, session, envelope, args, authdata):
        if authdata[0] == 'PLAIN':
            return await CustomAuthHandler.auth_PLAIN(server, authdata)
        else:
            return '535 Only PLAIN auth mechanism supported'

    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        fromaddr = envelope.mail_from
        if not address.endswith('@' + CONFIG['server_hostname']) and not fromaddr.endswith('@' + CONFIG['server_hostname']):
            return '550 not relaying from that domain'
        elif not address.endswith('@' + CONFIG['server_hostname']) and fromaddr.endswith('@' + CONFIG['server_hostname']):
            if not fromaddr in AUTHED_SESSIONS:
                return '530 U.AR Authorisation required'
        elif address.endswith('@' + CONFIG['server_hostname']) and fromaddr.endswith('@' + CONFIG['server_hostname']):
            if not fromaddr in AUTHED_SESSIONS:
                return '530 U.AR Authorisation required'
        elif address.endswith('@' + CONFIG['server_hostname']) and not fromaddr.endswith('@' + CONFIG['server_hostname']):
            pass
        else:
            return '530 U.UN Access restricted'
        envelope.rcpt_tos.append(address)
        if not is_user_mail_address_exists(address):
            return f'550 5.1.1 <{address}>: Recipient address rejected: User unknown'
        return '250 OK'

    async def handle_DATA(self, server, session, envelope):

        mime_message = message_from_string(envelope.content)
        subject_encoded = mime_message.get('Subject', 'No Subject')
        _, _, subject_base64 = subject_encoded.partition('?utf-8?b?')
        subject_decoded = base64.b64decode(subject_base64.encode(
            'utf-8')).decode('utf-8', errors='replace')
        if subject_decoded == '':
            subject_decoded = subject_encoded

        attachments = []
        blocked_attachments = []

        for part in mime_message.walk():
            if part.get_content_type() == 'text/plain':
                if part.get('Content-Transfer-Encoding') == 'base64':
                    decoded_text = base64.b64decode(
                        part.get_payload()).decode('utf-8', errors='replace')
                else:
                    decoded_text = part.get_payload()
            elif part.get_content_maintype() == 'multipart':
                continue
            else:
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if "attachment" in content_disposition or "inline" in content_disposition:
                    content_transfer_encoding = part.get(
                        'Content-Transfer-Encoding')
                    content = part.get_payload(decode=True)

                    if content_transfer_encoding == 'base64':
                        try:
                            try:
                                content = base64.b64decode(content)
                            except:
                                content = base64.b64decode(
                                    add_padding(content))
                        except:
                            pass

                    max_attachment_size = CONFIG['max_attachment_size'] * 1024 * 1024
                    if len(content) > max_attachment_size:
                        blocked_attachments.append(
                            f'{part.get_filename()} - {len(content) // (1024 * 1024)} MB')
                    else:
                        attachments.append({
                            'name': part.get_filename(),
                            'mime_type': content_type,
                            'content': content
                        })

        if not envelope.rcpt_tos[0].endswith('@' + CONFIG['server_hostname']):
            try:
                mdasend.send_mail(
                    envelope.mail_from, envelope.rcpt_tos[0], subject_decoded, decoded_text, attachments)
            except Exception as E:
                logging.error(str(E))
                return '554 5.4.0 Error: transaction failed'
        else:
            msg_id = str(uuid4())
            key = generator.randomkey()
            ADD_DATA = ''
            if not blocked_attachments == []:
                max_instr = str(CONFIG['max_attachment_size'])
                ADD_DATA = f'The following attachments were not received because their size exceeds the size set by the server ({max_instr} MiB):'
                for batt in blocked_attachments:
                    ADD_DATA = ADD_DATA + f'\n{batt}'
            try:
                save_message(
                    envelope.mail_from, envelope.rcpt_tos[0], subject_decoded, decoded_text+ADD_DATA, attachments, msg_id, key)
            except Exception as SE:
                logging.error(str(SE))
                return '500 Internal server error'

        return '250 Message accepted for delivery'


if __name__ == '__main__':
    handler = Handler()
    server = aiosmtpd.controller.Controller(
        handler, port=CPORT, server_hostname=CONFIG['server_hostname'], hostname=CONFIG['hostname'], tls_context=context, require_starttls=True, decode_data=True, enable_SMTPUTF8=True, auth_exclude_mechanism=['LOGIN'])
    banner.show()
    server.start()
    print('\n' + Fore.YELLOW +
          f"Server started on {Fore.CYAN}{CONFIG['hostname']}:{CONFIG['port']}{Fore.YELLOW}, press {Fore.RED}ENTER{Fore.YELLOW} to stop" + Fore.RESET + '\n')
    input()
    server.stop()
