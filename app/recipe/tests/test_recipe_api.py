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

