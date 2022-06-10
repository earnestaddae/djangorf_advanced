import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


pytestmark = pytest.mark.django_db

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(email='pholder@example.com', **kwargs):
    return get_user_model().objects.create_user(email, **kwargs)


class TestPublicUserAPI:
    def test_create_user_successful(self, client: APIClient):
        payload = {
            'email': 'testme@example.com',
            'password': 'passme123',
            'name': 'Test Me',
        }
        res = client.post(CREATE_USER_URL, data=payload)
        assert res.status_code == status.HTTP_201_CREATED
        user = get_user_model().objects.get(email=payload['email'])
        assert user.check_password(payload['password'])
        assert 'password' not in res.data

    def test_user_with_email_exists_error(self, client: APIClient):
        payload = {
            'email': 'testme@example.com',
            'password': 'passme123',
            'name': 'Test Me',
        }
        create_user(**payload)
        res = client.post(CREATE_USER_URL, data=payload)
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_too_short_error(self, client: APIClient):
        payload = {
            'email': 'testme@example.com',
            'password': 'pa',
        }
        res = client.post(CREATE_USER_URL, data=payload)
        user_exists = get_user_model().objects.filter(email=payload['email']).exists()
        assert user_exists == False

    def test_create_token_for_user(self, client: APIClient):
        user_details = {
            'name': "Test Name",
            'email': "testus@example.com",
            'password': 'passme123',
        }
        create_user(**user_details)
        payload = {
            'email': user_details['email'],
            'password': user_details['password']
        }
        res = client.post(TOKEN_URL, data=payload)
        assert res.status_code == status.HTTP_200_OK
        assert 'token' in res.data

    def test_create_token_bad_credentials(self, client: APIClient):
        create_user(email='tester@example.com', password='passme123')
        payload = {'email': 'tester@example.com', 'password': 'failed123'}
        res = client.post(TOKEN_URL, data=payload)
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert 'token' not in res.data

    def test_create_token_blank_password(self, client: APIClient):
        payload = {'email': 'tester@example.com', 'password': ''}
        res = client.post(TOKEN_URL, data=payload)
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert 'token' not in res.data

    def test_retrieve_user_unauthorized(self, client: APIClient):
        res = client.get(ME_URL)
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.fixture
def registered_user():
    user = create_user(
        email='tested@example.com',
        password='passme123',
        name='Tested Name',
    )
    return user

@pytest.fixture
def api_client(registered_user):
    client = APIClient()
    client.force_authenticate(user=registered_user)
    return client


class TestPrivateUserAPI:
    def test_retrieve_profile_success(self, registered_user, api_client):
        res = api_client.get(ME_URL)
        assert res.status_code == status.HTTP_200_OK
        assert res.data == {'name': registered_user.name, 'email': registered_user.email}

    def test_post_me_not_allowed(self, registered_user, api_client):
        res = api_client.post(ME_URL, {})
        assert res.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_update_user_profile(self, registered_user, api_client):
        payload = {'name': "Name Update", 'password': '123passme'}
        res = api_client.patch(ME_URL, payload)
        registered_user.refresh_from_db()
        assert registered_user.name == payload['name']
        assert registered_user.check_password(payload['password']) == True
        assert res.status_code == status.HTTP_200_OK
