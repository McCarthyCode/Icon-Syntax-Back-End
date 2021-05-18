from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.utils.translation import gettext_lazy as _

from rest_framework_simplejwt.tokens import RefreshToken


class UserManager(BaseUserManager):
    """
    Manager for User class as a whole, as oppposed to individual instances.
    """
    def create_user(self, username, email, password):
        """
        Creates and saves a User with the given username, email, and raw password.
        """
        user = self.model(
            username=username,
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, email, password):
        """
        Creates and saves a superuser with the given username, email, and raw password.
        """
        user = self.create_user(
            username,
            email,
            password,
        )

        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model including timestamps.
    """
    username = models.CharField(
        _('username'), max_length=64, unique=True, blank=False, default=None)
    email = models.EmailField(
        _('email address'),
        max_length=254,
        unique=True,
        blank=False,
        default=None)
    is_active = models.BooleanField(_('is active'), default=True)
    is_staff = models.BooleanField(_('is staff'), default=False)
    is_superuser = models.BooleanField(_('is superuser'), default=False)
    is_verified = models.BooleanField(_('is verified'), default=False)
    created = models.DateTimeField(_('datetime created'), auto_now_add=True)
    updated = models.DateTimeField(_('datetime updated'), auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'password']

    objects = UserManager()

    def __str__(self):
        """
        Returns a string describing the model instance.
        """
        return ' '.join(
            (
                self.username,
                self.email,
                'superuser' if self.is_superuser else \
                    'staff' if self.is_staff else 'user',
                'verified' if self.is_verified else 'unverified',
            ))

    @property
    def access(self):
        """
        Returns the user's access token.
        """
        return str(RefreshToken.for_user(self).access_token)

    @property
    def refresh(self):
        """
        Returns the user's refresh token.
        """
        return str(RefreshToken.for_user(self))

    @property
    def credentials(self):
        """
        Returns the user's username and email along with refresh and access tokens.
        """
        refresh = RefreshToken.for_user(self)

        return {
            'username': self.username,
            'email': self.email,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }
