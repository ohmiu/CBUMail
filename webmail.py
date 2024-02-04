from pywebio import config
from pywebio.input import *
from pywebio.output import *
from pywebio.session import *
from pywebio_battery import *
from pywebio.pin import *
from config import CONFIG as baseconf
from mda import MailDeliveryAgent as mdasend
from webmailconf import CONFIG as wmconf
import openapi, time, re, base64

config(title='WebMail', theme='dark')

def destruct():
    login, password = get_cookie('wmauthdata').split(':')
    openapi.delete_all_user_data(login)
    popup('Account fully removed', [put_success('Account has been removed from server.'), put_button('Ok', color='success', onclick=logout)], closable=False)
    

def account_remove():
    popup(
        'Account Deletion', [
            put_warning('Warning', 'When an account is deleted, all data will be physically deleted from the server with no possibility of recovery.'),
            put_button('Destroy my account', onclick=destruct, color='danger')
        ]
    )

def logout():
    set_cookie('wmauthdata', 'None', days=1)
    run_js('window.location.replace("/webmail?reload");')

def refresh():
    run_js('window.location.replace("/webmail?reload");')

def sendmail():

    def is_valid_email(email):
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if email_pattern.match(email):
            return True
        else:
            return False


    def send_mail(data):
        login, password = get_cookie('wmauthdata').split(':')
        if data['recipient'] == '':
            toast('The "recipient" field must be completed', color='error')
            close_popup()
            exit()
        if data['subject'] == '':
            data['subject'] = 'No subject'
        if data['text'] == '':
            data['text'] = 'No text'
        if data['subject'] == 'No subject' and data['text'] == 'No text' and data['files'] == []:
            toast('There are too few fields to fill in', color='error')
            close_popup()
            exit()
        if not is_valid_email(data['recipient']):
            toast('Incorrect recipient address', color='error')
            close_popup()
            exit()
        recipient = data['recipient']
        subject = data['subject']
        text = data['text']
        u_attachments = data['files']
        attachments = []
        for attachment in u_attachments:
            if attachment['mime_type'] == '':
                attachment['mime_type'] == 'application/octet-stream'
            attachments.append(
                {'name': attachment['filename'], 'mime_type': attachment['mime_type'], 'content': base64.b64encode(attachment['content'])}
            )
        if not recipient.endswith(f'@'+wmconf['maildomain']):
            password = None
        close_popup()
        mdasend.send_mail(login, recipient, subject, text, attachments, password)
        toast('Messages accepted for delivery')
        try:
            mdasend.send_mail(login, recipient, subject, text, attachments, password)
            toast('Messages accepted for delivery')
        except Exception as E:
            print(E)
            toast('Unckown error while sending message', color='error')
        
        
    data = popup_input([
        put_input("recipient", label="Recipient"),
        put_input('subject', label="Subject"),
        put_textarea('text', label='Text'),
        put_file_upload('files', label='Attachments upload', multiple=True, max_size=(1024 * 1024 * baseconf['max_attachment_size']))
    ], title='Send E-mail', validate=send_mail, cancelable=True)

def job(login, password):
    if get_query('msgid') == None and get_query('del') == None:
        put_html('<h1><img src="/static/wave.png" width="100" height="100" />WaveMail</h1>', scope='base')
        put_html(f'<p>Account: <code>{login}</code></p>', scope='base')
        put_button('> Send email', onclick=sendmail, link_style=True, scope='base')
        put_button('> Refresh', onclick=refresh, link_style=True, scope='base')
        put_button('> Logout', onclick=logout, link_style=True, scope='base')
        put_button('> Delete account data', onclick=account_remove, link_style=True, scope='base')
        put_loading(color='info', scope='loading')
        put_html('<h2>Mailbox</h2>', scope='mbox')
        messages = openapi.get_mailbox_messages(login)
        messages.reverse()
        if messages == []:
            put_text('Mailbox is empty', scope='mbox')
            clear('loading')
        else:
            achi=0
            for id in messages:
                achi=achi+1
                put_text()
                put_table([[put_html('<img src="/static/letter.png" width="35" height="35" />'), put_text(achi), put_link(f'{id.upper()}', f'/webmail?reload&msgid={id}')]])
            clear('loading')
    elif not get_query('del') == None:
        openapi.delete_message(login, get_query('del'))
        run_js('window.location.replace("/webmail?reload");')
    else:
        msg_id = get_query('msgid')
        if not msg_id in openapi.get_mailbox_messages(login):
            run_js('window.location.replace("/webmail?reload");')
            exit()
        put_html(f'<h1><img src="/static/wave.png" width="50" height="50" />WaveMail</h1><p>Message ID: <code>{msg_id}</code></p>', scope='base')
        put_table([[
            put_link('< Return back', '/webmail?reload', scope='base'),
            put_link('< Delete this message', f'/webmail?reload&del={msg_id}', scope='base')
        ]], scope='base')
        put_loading(scope='mbox', color='info')
        put_text('Decrypting message data...', scope='mbox')
        message = openapi.message(login, password, msg_id)
        clear('mbox')
        put_text(message.text, scope='mbox')
        if message.attachments == []:
            pass
        else:
            put_text('\n\nAttachments:', scope='mbox')
            for attachment in message.attachments:
                size = len(attachment['content'])
                put_table([[put_text(attachment['name']), put_text(str(size) + ' bytes'), put_file(attachment['name'], attachment['content'], scope='mbox', label='Download')]])



def main():
    if str(get_cookie('wmauthdata')) == 'None':
        run_js('window.location.replace("/login?reload");')
        exit()
    try:
        login, password = get_cookie('wmauthdata').split(':')
        if not openapi.check_password(login, password):
            raise Exception()
    except:
        run_js('window.location.replace("/login?reload");')
        exit()
    put_scope('base')
    put_scope('loading')
    put_scope('mbox')
    job(login, password)
