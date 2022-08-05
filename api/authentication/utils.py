from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.utils.translation import gettext_lazy as _


class Util:
    """
    Class defining utility methods.
    """

    @staticmethod
    def send_email(subject, body, to):
        """
        Sends a single email for basic use.
        """

        if not settings.SEND_EMAIL:
            return

        email = EmailMessage(subject=subject, body=body, to=to)
        email.send()

    @staticmethod
    def send_email_link(subject, body, user, path):
        """
        Sends a single email that contains an activation link.
        """

        if not settings.SEND_EMAIL:
            return

        if settings.STAGE == 'development':
            scheme = 'http'
            domain = 'localhost:8100'
        else:
            scheme = 'https'
            domain = 'iconsyntax.org'

        Util.send_email(
            subject,
            body + f'\n\n{scheme}://{domain}{path}/{user.access}\n\n' + _(
                'This activation code will expire in 30 minutes. If you believe you are receiving this message in error, please contact support at support@iconsyntax.org.'
            ),
            [user.email],
        )
