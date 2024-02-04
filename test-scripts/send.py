import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Параметры для подключения к SMTP серверу
smtp_server = '127.0.0.1'
smtp_port = 25

# Адреса отправителя и получателя
from_email = 'sus@sus.sus'
to_email = 'example@example.com'
smtp_password = 'test'

# Создаем MIME-сообщение
subject = 'Abobus niggers sex'
body = 'I want to send fucking english text'

message = MIMEMultipart()
message['From'] = from_email
message['To'] = to_email
message['Subject'] = subject
message.attach(MIMEText(body, 'plain'))

# Подключение к SMTP серверу и отправка письма
try:
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Установка защищенного TLS-соединения

        # Если требуется аутентификация, раскомментируйте следующие две строки
        # server.login(from_email, smtp_password)

        server.sendmail(from_email, to_email, message.as_string())
        print('Письмо успешно отправлено!')
except Exception as e:
    print(f'Ошибка при отправке письма: {e}')
