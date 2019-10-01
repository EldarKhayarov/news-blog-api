from django.db import models
from django.utils.translation import gettext_lazy as _


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(verbose_name=_('Date and time of creating'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Date and time of updating'), auto_now=True)

    class Meta:
        abstract = True
