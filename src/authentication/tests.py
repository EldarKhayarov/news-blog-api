import json
from typing import Any

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()


CONTENT_TYPE = 'application/json'


# Common methods could be used in other apps tests
URL_GET_TOKEN = reverse('api-auth:token-obtain-pair')
URL_REFRESH_TOKEN = reverse('api-auth:token-refresh')


# Just user for cases
USER = {
    'username': 'user',
    'password': 'f34ewf840hid9v8',
    'email': 'user@user.com',
}


def make_post_request(
        client: Any, path: str, data: dict
) -> dict:
    response = client.post(path=path, data=data, content_type=CONTENT_TYPE)

    response_content = json.loads(response.content)
    response_content['status_code'] = response.status_code

    return response_content


def get_tokens(
        client: Any, username: str, password: str
) -> dict:
    request_content = json.dumps({'username': username, 'password': password})
    return make_post_request(client, URL_GET_TOKEN, request_content)


def refresh_token(
    client: Any, token: str
) -> dict:
    request_content = json.dumps({'refresh': token})
    return make_post_request(client, URL_REFRESH_TOKEN, request_content)


class AuthUserGetRefreshTokenTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username=USER['username'],
            email=USER['email'],
            password=USER['password']
        )

        # is's important to give unhashed password
        self.user_data = {
            'password': USER['password'],
        }

    def test_user_get_token(self):
        response_content = get_tokens(
            username=self.user.username,
            password=self.user_data['password'],
            client=self.client
        )
        self.assertEqual(
            response_content['status_code'], 200,
            msg=response_content.get('detail'))

        self.assert_('access' in response_content.keys())
        self.assert_('refresh' in response_content.keys())

    def test_user_refresh_token(self):
        # get tokens
        get_token_response = get_tokens(
            client=self.client,
            username=self.user.username,
            password=self.user_data['password']
        )
        self.assertEqual(get_token_response['status_code'], 200)

        access = get_token_response['access']
        refresh = get_token_response['refresh']

        get_refresh_response = refresh_token(
            client=self.client, token=refresh
        )
        self.assertEqual(get_refresh_response['status_code'], 200)

        self.assert_('access' in get_refresh_response.keys())
        new_access = get_refresh_response['access']
        self.assertNotEqual(access, new_access)


class AuthEmailOrUsernameTestCase(APITestCase):
    """
    Test case for `Username or Email authentication` feature.
    """
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username=USER['username'],
            email=USER['email'],
            password=USER['password']
        )

        # is's important to give unhashed password
        self.user_data = {
            'password': USER['password'],
        }

    def try_to_get_token(self, username_email: str) -> dict:
        """
        Trying to get token for `username_email` user.
        :param username_email: user's username or email.
        :return: dict with response.
        """
        request_data = {
            'username': username_email,
            'password': self.user_data['password']
        }
        return make_post_request(
            client=self.client,
            data=json.dumps(request_data),
            path=URL_GET_TOKEN
        )

    def test_auth_username(self):
        """
        Right username will be given.
        Status code must be 200.
        :return: None
        """
        response = self.try_to_get_token(self.user.username)
        self.assertEqual(response['status_code'], 200)

    def test_auth_wrong_username(self):
        """
        Wrong username will be given.
        Status code must be 401.
        :return: None
        """
        response = self.try_to_get_token(self.user.username + 'f')
        self.assertEqual(response['status_code'], 401)

    def test_auth_email(self):
        """
        Right email will be given.
        Status code must be 200.
        :return: None
        """
        response = self.try_to_get_token(self.user.email)
        self.assertEqual(response['status_code'], 200)

    def test_auth_wrong_email(self):
        """
        Wrong email will be given.
        Status code must be 401.
        :return: None
        """
        response = self.try_to_get_token(self.user.email + 'm')
        self.assertEqual(response['status_code'], 401)

    def test_auth_wrong_password(self):
        """
        Wrong password.
        Status code must be 401.
        :return: None
        """
        response = get_tokens(
            client=self.client,
            username=self.user.email,
            password=self.user_data['password'] + 'f'
        )
        self.assertEqual(response['status_code'], 401)
