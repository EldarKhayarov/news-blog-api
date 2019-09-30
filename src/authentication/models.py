from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)

from core.models import TimestampedModel


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have a email.')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        return user


class User(PermissionsMixin, TimestampedModel, AbstractBaseUser):
    username = models.CharField(
        _("username"), max_length=32, unique=True, db_index=True
    )
    email = models.EmailField(_("user's email"), unique=True, db_index=True)
    is_active = models.BooleanField(_("user is active"), default=True)
    is_staff = models.BooleanField(_("user is staff"), default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.username

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username
