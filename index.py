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
    else:
        run_js('window.location.replace("/static/main/index.html");')
        exit()
