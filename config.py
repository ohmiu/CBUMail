CONFIG = {
    'hostname': '127.0.0.1',  # Server IP
    'server_hostname': 'example.com',  # Server @host.name
    'port': 25,  # Bind port
    'tls_cert_path': 'certs/cert.pem',  # TLS certificate path
    'tls_key_path': 'certs/key.pem',  # TLS certificate key path
    'database_path': 'databases/data.jxdb',  # Main database path
    'database_password': "mXxdrZc7uhN8zFDY",  # Database password
    'hash_algo': "sha3-256",  # You can use: sha256, sha3-256, md5, sha1, sha224
    'session_activity_time': 30,  # Authorization session lifetime
    'logging_level': 'warn',  # Available variables: all, warn
    'mda_use_only_verified_tls_certs': False, # Check whether TLS certificates belong to hosts (True or False)
    'max_attachment_size': 20 # Maximum attachment size in MiB
}
