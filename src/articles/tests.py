import json
from copy import deepcopy

from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from .serializers import ArticleCreateRetrieveSerializer, AuthorSerializer
from .models import Article
from core.utils import slugify_article


APPLICATION_JSON = 'application/json'
UserModel = get_user_model()

AUTHOR = {
    'username': 'author',
    'email': 'author@author.com',
    'password': 'sdfaFijf3w9',
}

USER = {
    'username': 'user',
    'email': 'user@user.com',
    'password': 'fi7f329HHGYf2'
}

ARTICLE = {
    'title': 'Test title',
    'description': 'Test description',
    'text': 'Test text',
    'preview_image': 'https://google.com',
    'resources': [
        {
            'url': 'https://google.com',
            'type': 'IMG'
        },
        {
            'url': 'https://google.com',
            'type': 'URL'
        },
        {
            'url': 'https://youtube.com',
            'type': 'VID'
        }
    ]
}

COMMENT = {
    'text': 'tst comment',
    'resources': [
        {
            'url': 'https://test-img.com',
            'type': 'IMG'
        },
        {
            'url': 'https://test-url.com',
            'type': 'URL'
        }
    ]
}


def grant_author(instance: UserModel):
    instance.is_staff = True


class ArticleCommentMixin:
    """
    Mixin with adding common attributes.
    """
    def set_up(self):
        self.url_article = reverse('articles:article-list')
        self.url_article_detail = reverse('articles:article-detail', kwargs={
            'slug': slugify_article(1, ARTICLE['title'])
        })
        # create an author that isn't a superuser
        self.author = UserModel.objects.create_user(**AUTHOR)
        grant_author(self.author)
        self.author.save()
        self.user = UserModel.objects.create_user(**USER)

    def create_article(self, data=ARTICLE):
        serializer = ArticleCreateRetrieveSerializer(data=data, context={'user': self.author})
        serializer.is_valid()
        serializer.save()


class ArticleTestCase(ArticleCommentMixin, APITestCase):
    def setUp(self) -> None:
        super().set_up()

    def test_article_create_article_success(self):
        self.client.force_authenticate(self.author)
        response = self.client.post(
            path=self.url_article,
            data=json.dumps(ARTICLE),
            content_type=APPLICATION_JSON
        )

        data = json.loads(response.content)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            str(response.status_code)+'\n'+str(data)
        )

    def test_article_create_wrong_article(self):
        self.client.force_authenticate(self.author)
        wrong_fields = ('title', 'text', 'description', 'preview_image')

        for f in wrong_fields:
            article = deepcopy(ARTICLE)
            article[f] = 'wrong' if f == 'preview_image' else ''
            response = self.client.post(
                path=self.url_article,
                data=json.dumps(article),
                content_type=APPLICATION_JSON
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
                str(response.status_code)+'\n'+str(json.loads(response.content))
            )

    def test_article_create_wrong_article_resource(self):
        self.client.force_authenticate(self.author)
        wrong_fields = ('url', 'type')

        for f in wrong_fields:
            article = deepcopy(ARTICLE)
            article['resources'][0][f] = 'wrong'
            response = self.client.post(
                path=self.url_article,
                data=json.dumps(article),
                content_type=APPLICATION_JSON
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
                str(response.status_code)+'\n'+str(response.content)
            )

    def test_article_create_article_permission_denied(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(
            path=self.url_article,
            data=ARTICLE,
            content_type=APPLICATION_JSON
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "CODE: " + str(response.status_code)
            )

    def test_article_update_article(self):
        self.client.force_authenticate(self.author)

        self.create_article()
        data = deepcopy(ARTICLE)
        data['resources'][1]['delete'] = 'true'
        data['resources'][0]['url'] = 'https://yandex.ru/'
        data['description'] = 'Updated description.'
        data['author'] = AuthorSerializer(self.author).data

        # Add IDs for updating
        for key, resource in enumerate(data['resources'], 1):
            resource['id'] = key

        response = self.client.put(
            path=self.url_article_detail,
            data=json.dumps(data),
            content_type=APPLICATION_JSON
        )

        response_content = json.loads(response.content)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            str(response.status_code) + '\n' + str(response_content) +
            '\n' + str(data)
        )

        # We can ignore read only and write only fields value,
        # because they're immutable
        response_content.pop('created_at')
        response_content.pop('comments')

        # And remove deleted objects
        data['resources'] = [
            res for res in data['resources'] if res.get('delete') is None
        ]
        self.assertEqual(
            response_content,
            data,
            "DATA: " + str(data) + '\n' + "RESPONSE: " + str(response_content)
        )

    def test_article_update_article_partial(self):
        self.client.force_authenticate(self.author)

        self.create_article()
        data = {
            'description': 'Partial description',
            'resources': [{
                'id': 1,
                'url': 'https://test.com/'
            }]
        }

        response = self.client.patch(
            path=self.url_article_detail,
            data=json.dumps(data),
            content_type=APPLICATION_JSON
        )
        response_content = json.loads(response.content)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            str(status) + '\n' + str(response_content)
        )

        # check content in server with our theory
        new_response = self.client.get(path=self.url_article_detail)
        new_response_content = json.loads(new_response.content)

        theoretical_response_content = deepcopy(ARTICLE)

        for key in new_response_content.keys():
            theoretical_response_content[key] = response_content[key]

        self.assertEqual(
            theoretical_response_content,
            new_response_content,
            "THEORY: " + str(theoretical_response_content) + "\n" + "RESPONSE: " + str(new_response_content)
        )

    def test_article_delete_success(self):
        self.client.force_authenticate(self.author)
        self.create_article()

        # Check creating
        response = self.client.get(path=self.url_article_detail)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            str(response.status_code) + '\n' + str(response.content)
        )

        # Delete
        response = self.client.delete(
            path=self.url_article_detail,
            content_type=APPLICATION_JSON
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            str(response.status_code) + '\n' + str(response.content)
        )

        # Check result
        deleted_article = Article.include_deleted.last()
        self.assertTrue(deleted_article.is_deleted)
        response = self.client.get(self.url_article_detail)
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            str(response.status_code) + '\n' + str(response.content)
        )


class CommentsTestCase(ArticleCommentMixin, APITestCase):
    def setUp(self) -> None:
        # Create author, user, url for article
        super().set_up()
        self.create_article()
        self.article = Article.objects.last()

        self.url_add_comment = reverse(
            'articles:article-detail',
            kwargs={'slug': self.article.slug}
        ) + 'add_comment/'

    def test_comment_create_success(self):
        self.client.force_authenticate(self.user)

        # Check there are not comments
        response = self.client.get(self.url_article_detail)
        resp_data = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp_data['comments']), 0, len(resp_data['comments']))

        # Create a comment
        response = self.client.post(
            self.url_add_comment,
            data=json.dumps(COMMENT),
            content_type=APPLICATION_JSON
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            str(response.status_code) + '\n' + str(json.loads(response.content))
        )

        # Check there is one comment
        response = self.client.get(self.url_article_detail)
        resp_data = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp_data['comments']), 1, len(resp_data['comments']))
