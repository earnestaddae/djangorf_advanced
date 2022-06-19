import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer


pytestmark = pytest.mark.django_db

TAGS_URL = reverse('recipe:tag-list')

def detail_url(tag_id):
    return reverse('recipe:tag-detail', args=[tag_id])


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


    def test_update_tag(self, api_client, tag_user):
        tag = Tag.objects.create(user=tag_user, name='Dinner')

        payload = {'name': 'Dessert'}
        url = detail_url(tag.id)

        res = api_client.patch(url, data=payload)
        tag.refresh_from_db()

        assert res.status_code == status.HTTP_200_OK
        assert tag.name == payload['name']

    def test_delete_tag(self, api_client, tag_user):
        tag = Tag.objects.create(user=tag_user, name='Breakfast')

        url = detail_url(tag.id)

        res = api_client.delete(url)
        tags = Tag.objects.filter(user=tag_user)
        assert res.status_code == status.HTTP_204_NO_CONTENT
        assert tags.exists() == False

    def test_filter_tags_assigned_to_recipes(self, api_client, tag_user):
        tag1 = Tag.objects.create(user=tag_user, name='Breakfast')
        tag2 = Tag.objects.create(user=tag_user, name='Brunch')
        recipe = Recipe.objects.create(title='Muffins', time_minutes=4, price=Decimal('4.3'), user=tag_user)
        recipe.tags.add(tag1)

        res = api_client.get(TAGS_URL, {'assigned_only': 1})
        assert res.status_code == status.HTTP_200_OK

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)

        assert s1.data in res.json()
        assert s2.data not in res.json()

    def test_filtered_unique_tags(self, api_client, tag_user):
        tag = Tag.objects.create(user=tag_user, name='Lunch')
        Tag.objects.create(user=tag_user, name='Dinner')
        recipe1 = Recipe.objects.create(title='Pork soup', time_minutes=4, price=Decimal('4.3'), user=tag_user)
        recipe2 = Recipe.objects.create(title='Beef soup', time_minutes=4, price=Decimal('4.1'), user=tag_user)
        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = api_client.get(TAGS_URL, {'assigned_only': 1})
        assert len(res.data) == 1




