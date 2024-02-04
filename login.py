from pywebio.input import *
from pywebio.output import *
from pywebio.session import *
from pywebio import config
from pywebio_battery import *
from webmailconf import CONFIG as wmconf
from utils import SymmetricEncryption as senc
import openapi
import hashlib

config(title='Login / WebMail', theme='dark')


def check_form(data):
    login = data['login'] + '@' + wmconf['maildomain']
    password = data['password']
    if openapi.check_password(login, password):
        set_cookie('wmauthdata', f'{login}:{password}', days=1)
        run_js('window.location.replace("/webmail?reload");')
    else:
        toast('Incorrect password, try again.', color='error')
        job()


def job():
    data = input_group("Log in", [
        input('Enter your login', name='login', required=True,
              help_text='Numbers and Latin characters only, max length: 24', placeholder='exampleuser'),
        input('Enter your password', name='password',
              type=PASSWORD, required=True, help_text='Numbers and Latin characters only', placeholder='************')
    ], validate=check_form)


def main():
    put_html('<h1><img src="/static/wave.png" width="100" height="100" />WaveMail - Sign In</h1>')
    put_link('< Main page', '/?reload')
    put_scope('base')
    if not str(get_cookie('wmauthdata')) == 'None':
        run_js('window.location.replace("/webmail?reload");')
        exit()
    job()
