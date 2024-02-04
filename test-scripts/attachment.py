import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import base64

# Информация о сервере SMTP и учетные данные
smtp_server = '127.0.0.1'
smtp_port = 25
smtp_username = 'example@example.com'
smtp_password = 'test'

# Отправитель и получатель
sender_email = 'vasko@test.bb'
recipient_email = 'example@example.com'

# Создание объекта MIMEMultipart
message = MIMEMultipart()
message['From'] = sender_email
message['To'] = recipient_email
message['Subject'] = 'Тема письма'

# Текст письма
body = 'Привет, это текст письма.'
message.attach(MIMEText(body, 'plain'))

# Вложение
attachment_path = 'pic.png'
attachment = open(attachment_path, 'rb').read()
attachment = base64.b64encode(attachment)

# Создание объекта MIMEBase
part = MIMEBase('application', 'octet-stream')
part.set_payload(attachment)
encoders.encode_base64(part)
part.add_header('Content-Disposition',
                f'attachment; filename= {attachment_path}')

# Прикрепление вложения к письму
message.attach(part)

# Установка соединения с SMTP-сервером и отправка письма
with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.ehlo()
    server.starttls()
    # server.login(smtp_username, smtp_password)
    server.sendmail(sender_email, recipient_email, message.as_string())

print('Письмо успешно отправлено!')
