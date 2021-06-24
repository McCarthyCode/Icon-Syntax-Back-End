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
        email = EmailMessage(subject=subject, body=body, to=to)
        email.send()

    @staticmethod
    def send_email_link(subject, body, user, path):
        """
        Sends a single email that contains an activation link.
        """
        if settings.STAGE == 'development':
            scheme = 'http'
            domain = 'localhost:8000'
        else:
            scheme = 'https'
            domain = get_current_site(request).domain
        query_string = f'?access={user.access}'

        Util.send_email(
            subject,
            body + f'\n\n{scheme}://{domain}{path}{query_string}\n\n' + _(
                'This activation code will expire in 30 minutes. If you believe you are receiving this message in error, please contact support at support@iconsyntax.org.'
            ),
            [user.email],
        )
