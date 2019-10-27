from django.template.defaultfilters import slugify as default_slugify
from unidecode import unidecode


def slugify(raw_text: str) -> str:
    """
    Transliterated non-ascii characters and returns slug.
    :param raw_text: string you want to slugify
    :return: slug
    """
    return default_slugify(unidecode(raw_text))


def slugify_article(article_id: int, article_title: str) -> str:
    """
    Returns slug for articles by template: 'article_id-article_title'.
    :param article_id:
    :param article_title:
    :return: slug
    """
    return str(article_id) + '-' + slugify(article_title)
