# Alpha - CBUMail - Secure and Privacy-Focused Email Server

CBUMail is an integrated email server that combines SMTP (Simple Mail Transfer Protocol), WebMail, and MDA (Mail Delivery Agent). It is designed with a primary focus on ensuring maximum security and privacy for users. The server is written in Python 3, making it modern, efficient, and easy to deploy.

## Features

- **SMTP Support:** CBUMail facilitates the transfer of emails between servers using the industry-standard SMTP protocol.

- **WebMail Interface:** A user-friendly WebMail interface is included, providing a convenient way for users to access their emails through a web browser.

- **MDA Functionality:** The Mail Delivery Agent ensures efficient delivery of emails to the recipient's mailbox.

- **TLS Technology:** CBUMail incorporates Transport Layer Security (TLS) technology to encrypt communications between servers and clients. This ensures a secure and private email communication environment.

## Security and Privacy

CBUMail places a strong emphasis on security and privacy, offering the following safeguards:

- **TLS Encryption:** All communications, including emails in transit and user interactions with the WebMail interface, are encrypted using TLS. This encryption helps protect sensitive information from unauthorized access.

- **End-To-End Encryption:** RSA is used in conjunction with ChaCha20-poly1305 to protect the mailbox from 3rd party access, no one but the WebMail user can access the mailbox and decrypt the emails.

- **Secure Deployment:** The server is designed to be deployed in a secure manner.

## Deployment

CBUMail is easy to deploy, thanks to its Python 3 implementation. The server can be set up on various platforms.
