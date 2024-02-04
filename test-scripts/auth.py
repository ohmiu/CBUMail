import smtplib
import ssl

smtp_server = '127.0.0.1'
smtp_port = 25
smtp_username = 'test@example.com'
smtp_password = 'test'

try:
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
        server.ehlo()
        server.starttls(context=context)
        server.login(smtp_username, smtp_password)
        print('Авторизация успешна!')
except Exception as e:
    print(f'Ошибка при авторизации: {e}')
