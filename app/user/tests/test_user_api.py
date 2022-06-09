import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


pytestmark = pytest.mark.django_db

CREATE_USER_URL = reverse('user:create')


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
