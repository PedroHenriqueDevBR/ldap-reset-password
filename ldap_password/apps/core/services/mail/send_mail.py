from django.conf import settings

# from django.core.mail import send_mail
import smtplib
import email.utils
from email.message import EmailMessage
import ssl


class CustomMailBackend:
    def send_mail(self, subject: str, message: str, to: str) -> None:
        SENDERNAME = "Não Responda"
        RECIPIENT = to
        SENDER = settings.DEFAULT_FROM_EMAIL
        USERNAME_SMTP = settings.EMAIL_HOST_USER
        password_smtp = settings.EMAIL_HOST_PASSWORD
        HOST = settings.EMAIL_HOST
        PORT = settings.EMAIL_PORT
        SUBJECT = subject

        # The email body for recipients with non-HTML email clients.
        BODY_TEXT = (
            "Defensoria Pública do Estado do Piauí\r\n"
            + "Esse é um e-mail confidencial, não o repasse para ninguém.\n"
            + message
        )

        # The HTML body of the email.
        BODY_HTML = """<html>
        <head></head>
        <body>
        <h1>Defensoria Pública do Estado do Piauí</h1>
        <p>
            Esse é um e-mail confidencial, não o repasse para ninguém.<br>
            {}
        </p>
        </body>
        </html>""".format(
            message
        )

        msg = EmailMessage()
        msg["Subject"] = SUBJECT
        msg["From"] = email.utils.formataddr((SENDERNAME, SENDER))
        msg["To"] = RECIPIENT

        msg.add_alternative(BODY_TEXT, subtype="text")
        msg.add_alternative(BODY_HTML, subtype="html")

        try:
            server = smtplib.SMTP(HOST, PORT)
            server.ehlo()
            server.starttls(
                context=ssl.create_default_context(
                    purpose=ssl.Purpose.SERVER_AUTH, cafile=None, capath=None
                )
            )
            server.ehlo()
            server.login(USERNAME_SMTP, password_smtp)
            server.sendmail(SENDER, RECIPIENT, msg.as_string())
            server.close()
        except Exception as e:
            print(f"Error: {e}")
        else:
            print("Email successfully sent!")


class MailService:
    def __init__(self) -> None:
        self.mail_service = CustomMailBackend()

    def send_token(self, to: str, token: str) -> None:
        subject = "NO REPPLY"
        mail_body = "Token para recuperação de senha: {}".format(token)
        self.mail_service.send_mail(
            subject=subject,
            message=mail_body,
            to=to,
        )
        # send_mail(
        #     subject=subject,
        #     message=mail_body,
        #     from_email=settings.EMAIL_HOST_USER,
        #     recipient_list=[
        #         to,
        #     ],
        #     fail_silently=False,
        # )

    def send_password(self, to: str, password: str) -> None:
        subject = "NO REPPLY"
        mail_body = (
            "Sua nova senha: {}, redefina a senha de acordo com a sua escolha!".format(
                password,
            )
        )
        self.mail_service.send_mail(
            subject=subject,
            message=mail_body,
            to=to,
        )
        # send_mail(
        #     subject=subject,
        #     message=mail_body,
        #     from_email=settings.EMAIL_HOST_USER,
        #     recipient_list=[
        #         to,
        #     ],
        #     fail_silently=False,
        # )
