from django.conf import settings
from django.core.mail import send_mail


class MailService:
    def send_token(self, to: str, token: str) -> None:
        subject = "NO REPPLY"
        mail_body = "Token to reset account password: {}".format(token)
        send_mail(
            subject=subject,
            message=mail_body,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[
                to,
            ],
            fail_silently=False,
        )

    def send_password(self, to: str, password: str) -> None:
        subject = "NO REPPLY"
        mail_body = "Your new password: {}, change your password!".format(
            password,
        )
        send_mail(
            subject=subject,
            message=mail_body,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[
                to,
            ],
            fail_silently=False,
        )
