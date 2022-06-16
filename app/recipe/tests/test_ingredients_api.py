import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


pytestmark = pytest.mark.django_db

INGREDIENTS_URL = reverse('recipe:ingredient-list')

def detail_url(ingredient_id):
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


@pytest.fixture
def ingredient_user():
    email = 'testme@example.com'
    password = 'passme123'
    user = get_user_model().objects.create_user(
        email=email,
        password=password,
    )
    return user

@pytest.fixture
def api_client(ingredient_user):
    client = APIClient()
    client.force_authenticate(user=ingredient_user)
    return client



class TestPublicIngredientsAPI:

    def test_auth_required(self):
        client = APIClient()
        res = client.get(INGREDIENTS_URL)
        assert res.status_code == status.HTTP_401_UNAUTHORIZED


class TestPrivateIngredientsAPI:

    def test_retrieve_ingredients(self, api_client, ingredient_user):
        for name in ('Kale', 'Vanilla'):
            Ingredient.objects.create(user=ingredient_user, name=name)

        res = api_client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    def test_ingredients_limited_to_user(self, api_client, ingredient_user):
        user2 = get_user_model().objects.create_user(email='user2@example.com', password='passmeuser')
        Ingredient.objects.create(user=user2, name='Milk')
        ingredient = Ingredient.objects.create(user=ingredient_user, name='Salt')

        res = api_client.get(INGREDIENTS_URL)

        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) == 1
        assert res.data[0]['name'] == ingredient.name
        assert res.data[0]['id'] == ingredient.id

    def test_update_ingredient(self, api_client, ingredient_user):
        ingredient = Ingredient.objects.create(user=ingredient_user, name='Pear')
        payload = {'name': 'Orange'}

        url = detail_url(ingredient.id)

        res = api_client.patch(url, data=payload)
        assert res.status_code == status.HTTP_200_OK
        ingredient.refresh_from_db() # required to refresh the database.
        assert ingredient.name == payload['name']

    def test_delete_ingredient(self, api_client, ingredient_user):
        ingredient = Ingredient.objects.create(user=ingredient_user, name='Mango')

        url = detail_url(ingredient.id)

        res = api_client.delete(url)

        assert res.status_code == status.HTTP_204_NO_CONTENT
        ingredients = Ingredient.objects.filter(user=ingredient_user)
        assert ingredients.exists() == False


































