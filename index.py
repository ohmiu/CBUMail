from pywebio.output import *
from pywebio import config
from pywebio_battery import *
from pywebio.session import *
import time

config(title='Hello / WebMail', theme='dark')


def main():
    put_scope('base')
    if not str(get_cookie('wmauthdata')) == 'None':
        run_js('window.location.replace("/webmail?reload");')
        exit()
    put_html('<h1>Welcome!<h1>', scope='base')
    time.sleep(1)
    clear('base')
    put_html('<h1><img src="/static/wave.png" width="100" height="100" />WaveMail</h1>', scope='base')
    put_link('Register', '/register')
    put_text('')
    put_link('Login', '/login')
