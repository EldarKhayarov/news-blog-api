from django.contrib import admin

from .models import Article, Comment, Resource


class CommentArticleInline(admin.TabularInline):
    model = Comment


class ResourceArticleInline(admin.TabularInline):
    model = Resource
    exclude = ('comment', 'is_deleted')


class ArticleAdmin(admin.ModelAdmin):
    inlines = (ResourceArticleInline, CommentArticleInline,)
    readonly_fields = ('slug',)
    exclude = ('is_deleted',)


admin.site.register(Article, ArticleAdmin)
