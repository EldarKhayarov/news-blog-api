from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from core.models import TimestampedModel, DeletableModel
from core.utils import slugify_article

UserModel = get_user_model()


RESOURCE_TYPES = (
    ('IMG', _('Image')),
    ('VID', _('Video')),
    ('URL', _('URL')),
)


class Article(TimestampedModel, DeletableModel):
    title = models.CharField(_("Article header"), max_length=150)
    description = models.TextField(_("Article description"), max_length=1000)
    text = models.TextField(_("Article text"))
    preview_image = models.URLField(_('Preview image of the article'))
    slug = models.SlugField(
        max_length=150,
        unique=True,
        allow_unicode=True,
        db_index=True
    )
    author = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='articles'
    )

    class Meta:
        verbose_name = _('article')
        verbose_name_plural = _('articles')
        ordering = ('-created_at',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify_article(self.id, self.title)
        return super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()

    def get_absolute_url(self):
        return reverse(
            'articles:article-detail',
            kwargs={'slug': self.slug}
            )


class Comment(TimestampedModel, DeletableModel):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(_('Comment text'), max_length=512)

    class Meta:
        verbose_name = _('comment')
        verbose_name_plural = _('comments')
        ordering = ('-created_at',)


class Resource(DeletableModel):
    url = models.URLField(_('Image URL'))
    type = models.CharField(
        _('Resources'),
        max_length=3,
        choices=RESOURCE_TYPES
    )
    article = models.ForeignKey(
        Article,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='resources',
        db_index=True
    )
    comment = models.ForeignKey(
        Comment,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='resources',
        db_index=True
    )

    class Meta:
        verbose_name = _('image')
        verbose_name_plural = _('images')
