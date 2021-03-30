from django.core.mail import EmailMessage


class Util:
    @staticmethod
    def send_email(subject, body, to):
        email = EmailMessage(subject=subject, body=body, to=to)
        email.send()
