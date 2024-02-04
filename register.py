import re
import os
import openapi
from pywebio.output import *
from pywebio.input import *
from pywebio import config
from pywebio_battery import *
from pywebio.session import *
from webmailconf import CONFIG as wmconf
from config import CONFIG
from jxdb import JsonDB

DB_PASS = CONFIG['database_password']
DB_PATH = CONFIG['database_path']

config(title='Register / WebMail', theme='dark')


def check_login(input_string, max_length=24):
    pattern = re.compile("^[a-zA-Z]+$")
    return bool(pattern.match(input_string)) and len(input_string) <= max_length


def check_password(input_string):
    pattern = re.compile("^[a-zA-Z0-9]+$")
    return bool(pattern.match(input_string))


def check_form(data):
    if check_login(data['login']) and check_password(data['password']):
        put_loading(scope='base', color='info')
        put_text('Creating, please stand by...', scope='base')
        spath = wmconf['adduser_script_path']
        login = data['login']
        password = data['password']
        maildomain = wmconf['maildomain']
        if not os.path.exists(DB_PATH):
            def create_db():
                db = JsonDB()
                db.save(DB_PATH, DB_PASS)
            create_db()
        if openapi.is_mailbox_exists(f'{login}@{maildomain}'):
            clear('base')
            popup('Validation error', [put_error(
                'This mailbox already exists.'), put_link('Retry', '/register?reload')], closable=False)
            exit()
        result = os.popen(
            f'python {spath} {login}@{maildomain} {password}').read()
        if '[+]' in result:
            clear('base')
            popup('Success', [put_success(
                f'User {login}@{maildomain} created successfully'), put_link('Login', '/login?reload')], closable=False)
        else:
            clear('base')
            popup(
                'Error', [put_error('Creation error, contact website administrator.')], closable=False)
    else:
        popup('Validation error', [put_error(
            'Use only Latin numerals and characters, maximum login length: 24.'), put_link('Retry', '/register?reload')], closable=False)


def main():
    put_html('<h1><img src="/static/wave.png" width="100" height="100" />WaveMail Register</h1>')
    put_link('< Main page', '/?reload')
    put_scope('base')
    if not str(get_cookie('wmauthdata')) == 'None':
        run_js('window.location.replace("/webmail?reload");')
        exit()
    if wmconf['register'] == False:
        return put_error('Registration disabled', 'The server administrator has disabled the ability to register.')
    data = input_group("Register", [
        input('Enter your login', name='login', required=True,
              help_text='Numbers and Latin characters only, max length: 24', placeholder='exampleuser'),
        input('Enter your password', name='password',
              type=PASSWORD, required=True, help_text='Numbers and Latin characters only', placeholder='StrongPassword100AAAtest')
    ], validate=check_form)
