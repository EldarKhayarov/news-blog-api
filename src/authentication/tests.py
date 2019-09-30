import json
import datetime
from typing import Type, Any

from rest_framework.test import APITestCase
from django.urls import reverse

from authentication.models import User


CONTENT_TYPE = 'application/json'


# Common methods could be used in other apps tests
URL_GET_TOKEN = reverse('api-auth:token-obtain-pair')
URL_REFRESH_TOKEN = reverse('api-auth:token-refresh')


def make_post_request(
        client: Any, path: str, data: dict
) -> dict:
    response = client.post(path=path, data=data, content_type=CONTENT_TYPE)

    response_content = json.loads(response.content)
    response_content['status_code'] = response.status_code

    return response_content


def get_tokens(
        client: Any, email: str, password: str
) -> dict:
    request_content = json.dumps({'email': email, 'password': password})
    return make_post_request(client, URL_GET_TOKEN, request_content)


def refresh_token(
    client: Any, token: str
) -> dict:
    request_content = json.dumps({'refresh': token})
    return make_post_request(client, URL_REFRESH_TOKEN, request_content)


# Just users for cases
USER = {
    'username': 'user',
    'password': 'f34ewf840hid9v8',
    'email': 'user@user.com',
}

USER_NO_TOKEN = {
    'username': 'user_no_token',
    'password': 'f32rfewfjiu98PFD8',
    'email': 'usernotoken@user.com',
}


class AuthUserTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username=USER['username'],
            email=USER['email'],
            password=USER['password']
        )
        self.user_no_token = User.objects.create_user(
            username=USER_NO_TOKEN['username'],
            password=USER_NO_TOKEN['password'],
            email=USER_NO_TOKEN['email']
        )

        self.user_data = {}
        self.user_no_token_data = {}

        self.user_data['password'] = USER['password']
        self.user_no_token_data['password'] = USER_NO_TOKEN['password']

    def test_user_get_token(self):
        # is's important to give unhashed password
        response_content = get_tokens(
            email=self.user.email,
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
            email=self.user.email,
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
