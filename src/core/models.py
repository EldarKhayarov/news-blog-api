from django.db import models
from django.utils.translation import gettext_lazy as _


class ExcludeDeletedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(verbose_name=_('Date and time of creating'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Date and time of updating'), auto_now=True)

    class Meta:
        abstract = True


class DeletableModel(models.Model):
    is_deleted = models.BooleanField(verbose_name=_('Object is deleted.'), default=False)

    objects = ExcludeDeletedManager()
    include_deleted = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()
