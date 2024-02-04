from pywebio.platform import path_deploy_http
from webmailconf import CONFIG

HOST = CONFIG['host']
PORT = CONFIG['port']

path_deploy_http('.', port=PORT, host=HOST, static_dir='static')
