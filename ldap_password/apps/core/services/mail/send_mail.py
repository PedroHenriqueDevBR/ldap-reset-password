from django.conf import settings
from django.core.mail import send_mail


class MailService:
    def send_mail(self, to: str, token: str) -> None:
        subject = "DPE-PI - NO REPPLY"
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
