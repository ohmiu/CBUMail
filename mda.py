import platform
import os
import random
import socket
import logging
import smtplib
import ssl
from config import CONFIG
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

logging.basicConfig(level=logging.WARNING,
                    format='[ MailDeliveryAgent ] - [%(levelname)s] - %(message)s')


def is_port_open(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host, port))
    sock.close()
    if result == 0:
        logging.info(f'Port {port} accessible, using')
        return True
    else:
        logging.error(f'Port {port} inaccessible, skipping')
        return False

def check_smtp_tls_support(smtp_server, smtp_port):
    try:
        logging.info('Checking TLS support')
        context = ssl.create_default_context()
        if CONFIG['mda_use_only_verified_tls_certs'] == False:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls(context=context)
            server.ehlo()
            server.quit()
            logging.info('TLS supported')
            return True
    except Exception as e:
        logging.error('TLS unsupported - ' + str(e))
        return False

class dig:
    def lookup(hostname: str):
        if platform.system() == 'Windows':
            logging.info('Using Windows dig resolver')
            data = os.popen(
                f'.\windig\dig.exe @1.1.1.1 mx {hostname} +short').read().split('\n')
        else:
            logging.info('Using Linux dig resolver')
            data = os.popen(
                f'dig @1.1.1.1 mx {hostname} +short').read().split('\n')
        CA = []
        for i in data:
            if ' ' in i:
                _, server = i.split(' ')
                CA.append(server)
        servers_count = str(len(CA))
        if not CA == []:
            logging.info(f'Resolved {servers_count} server(s)')
        else:
            logging.error('No servers found')
        return CA



class MailDeliveryAgent:

    def send_mail(sender_addr: str, recipient_addr: str, subject: str, message_body: str, attachments=[], password=None):
        _, recipient_domain = recipient_addr.split('@')
        mxservers = dig.lookup(recipient_domain)
        if not mxservers == []:
            mxserver = random.choice(mxservers)
            logging.info(f'Choosed {mxserver}')

            for port in [25, 465, 587]:
                if is_port_open(mxserver, port):
                    RPORT=port
                    break
                RPORT=None
            if RPORT == None:
                return logging.error('No MX servers available')
            if not check_smtp_tls_support(mxserver, RPORT):
                return logging.critical('Can not send email - TLS error')

        message = MIMEMultipart()
        message['From'] = sender_addr
        message['To'] = recipient_addr
        message['Subject'] = subject

        message.attach(MIMEText(message_body, 'plain'))

        for attachment in attachments:
            attachment_name = attachment.get('name', 'attachment')
            attachment_mime_type = attachment.get('mime_type', 'application/octet-stream')
            attachment_content = attachment.get('content', b'')

            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment_content)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={attachment_name}')
            message.attach(part)

        try:

            with smtplib.SMTP(mxserver, RPORT) as server:
                server.starttls()
                server.ehlo()
                if not password == None:
                    server.login(sender_addr, password)
                server.sendmail(sender_addr, recipient_addr, message.as_string())

            logging.info('Email sent successfully')
        except Exception as e:
            logging.error(f'Error sending email: {e}')
