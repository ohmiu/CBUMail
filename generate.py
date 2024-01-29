from OpenSSL import crypto
from datetime import datetime, timedelta


def generate_self_signed_certificate(key_file_path, cert_file_path, subject_name='localhost', valid_days=365):

    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 4096)


    cert = crypto.X509()
    cert.get_subject().CN = subject_name
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)

    cert.gmtime_adj_notAfter(valid_days * 24 * 60 * 60)

    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')

    with open(key_file_path, 'wb') as key_file:
        key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

    with open(cert_file_path, 'wb') as cert_file:
        cert_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))


key_file_path = 'certs/key.pem'
cert_file_path = 'certs/cert.pem'

generate_self_signed_certificate(key_file_path, cert_file_path)
