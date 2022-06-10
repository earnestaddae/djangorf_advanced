import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag

from recipe.serializers import TagSerializer


pytestmark = pytest.mark.django_db

TAGS_URL = reverse('recipe:tag-list')

@pytest.fixture
def tag_user():
    email = 'testme@example.com'
    password = 'passme123'
    user = get_user_model().objects.create_user(
        email=email,
        password=password,
    )
    return user

@pytest.fixture
def api_client(tag_user):
    client = APIClient()
    client.force_authenticate(user=tag_user)
    return client


class TestPublicTagAPI:

    def test_auth_required(self, client):
        client = APIClient()
        res = client.get(TAGS_URL)
        assert res.status_code == status.HTTP_401_UNAUTHORIZED


class TestPrivateTagAPI:
    def test_retrieve_tags(self, api_client, tag_user):
        for tag in ('Vegan', 'Meat'):
            Tag.objects.create(user=tag_user, name=tag)

        res = api_client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    def test_tags_limited_to_user(self, api_client, tag_user):
        new_user = get_user_model().objects.create_user('newme@example.com', 'passnew')
        Tag.objects.create(user=new_user, name='Salad')
        tag = Tag.objects.create(user=tag_user, name='Vegetarian')

        res = api_client.get(TAGS_URL)

        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) == 1
        assert res.data[0]['name'] == tag.name
        assert res.data[0]['id'] == tag.id




