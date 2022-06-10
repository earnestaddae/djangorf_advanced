import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


pytestmark = pytest.mark.django_db

RECIPES_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])

def create_recipe(user, **kwargs):
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 7,
        'price': Decimal('8.79'),
        'description': 'Sample recipe description',
        'link': 'http://example.com/recipe.pdf',
    }
    defaults.update(kwargs)
    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe

@pytest.fixture
def recipe_user():
    user = get_user_model().objects.create_user(
        email='tested@example.com',
        password= 'passme123',
    )
    return user

@pytest.fixture
def api_client(recipe_user):
    client = APIClient()
    client.force_authenticate(user=recipe_user)
    return client




class TestPublicRecipeAPI:

    def test_auth_required(self, client):
        client = APIClient()
        res = client.get(RECIPES_URL)
        assert res.status_code == status.HTTP_401_UNAUTHORIZED


class TestPrivateRecipeAPI:
    def test_retrieve_recipes(self, api_client, recipe_user):
        create_recipe(user=recipe_user)
        create_recipe(user=recipe_user)
        # api_client.force_authenticate(user=recipe_user)
        res = api_client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    def test_recipe_list_limited_to_user(self, api_client, recipe_user):
        other_user = get_user_model().objects.create_user(email='other@example.com', password='other123')
        create_recipe(user=other_user)
        create_recipe(user=recipe_user)
        res = api_client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=recipe_user)
        serializer = RecipeSerializer(recipes, many=True)
        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    def test_get_recipe_detail(self, api_client, recipe_user):
        recipe = create_recipe(user=recipe_user)

        url = detail_url(recipe.id)
        res = api_client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    def test_create_recipe(self, api_client, recipe_user):
        payload = {
            'title': 'Sample recipe title',
            'time_minutes': 7,
            'price': Decimal('8.79'),
            'description': 'Sample recipe description',
            'link': 'http://example.com/recipe.pdf',
        }
        res = api_client.post(RECIPES_URL, data=payload)
        assert res.status_code == status.HTTP_201_CREATED
        recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            assert getattr(recipe, k) == v
        assert recipe.user == recipe_user

    def test_partial_update(self, api_client, recipe_user):
        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(
            user=recipe_user,
            title='Sample recipe title',
            link=original_link,
        )
        payload = {'title': 'Changed Sample recipe title'}
        url = detail_url(recipe.id)
        res = api_client.patch(url, data=payload)
        assert res.status_code == status.HTTP_200_OK
        recipe.refresh_from_db() # required for test db refresh
        assert recipe.title == payload['title']
        assert recipe.link == original_link
        assert recipe.user == recipe_user

    def test_full_update(self, api_client, recipe_user):
        recipe = create_recipe(
            user=recipe_user,
            title='Sample recipe title',
            link='https://example.com/recipe.pdf',
            description='Lorem ipsum is a thing in published',
        )
        payload = {
            'title': 'Title changed',
            'link': 'https:/example.com/update-recipe.pdf',
            'description': 'Lorem changed la!',
            'time_minutes': 6,
            'price': Decimal('7.98'),
        }
        url = detail_url(recipe.id)
        res = api_client.put(url, data=payload)
        assert res.status_code == status.HTTP_200_OK
        recipe.refresh_from_db()
        for k, v in payload.items():
            assert getattr(recipe, k) == v
        assert recipe.user == recipe_user

    def test_update_user_returns_error(self, api_client, recipe_user):
        new_user = get_user_model().objects.create_user(email='newme@example.com', password='newme123')
        recipe = create_recipe(user=recipe_user)

        payload = {'user': new_user.id }
        url = detail_url(recipe.id)
        res = api_client.patch(url, data=payload)
        recipe.refresh_from_db()
        assert res.status_code == status.HTTP_200_OK
        assert recipe.user == recipe_user

    def test_delete_recipe(self, api_client, recipe_user):
        recipe = create_recipe(user=recipe_user)
        url = detail_url(recipe.id)
        res = api_client.delete(url)
        assert res.status_code == status.HTTP_204_NO_CONTENT
        assert Recipe.objects.filter(id=recipe.id).exists() == False

    def test_delete_recipe_other_user_error(self, api_client, recipe_user):
        other_user = get_user_model().objects.create_user(email='other@example.com', password='other123')
        recipe = create_recipe(user=other_user)
        url = detail_url(recipe.id)

        res = api_client.delete(url)

        assert res.status_code == status.HTTP_404_NOT_FOUND
        assert Recipe.objects.filter(id=recipe.id).exists() == True



