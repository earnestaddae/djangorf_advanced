import pytest

from django.contrib.auth import get_user_model
from decimal import Decimal

from core import models

pytestmark = pytest.mark.django_db

@pytest.fixture
def create_user():
    email = 'testme@example.com'
    password = 'passme123'
    user = get_user_model().objects.create_user(
        email=email,
        password=password,
    )
    return user


class TestModel:

    def test_create_user_with_email_successful(self, create_user):
        assert create_user.email == 'testme@example.com'
        assert create_user.check_password('passme123') == True

    def test_new_user_without_email_raises_error(self):
        with pytest.raises(ValueError):
            get_user_model().objects.create_user('', 'falsepass')

    def test_create_superuser(self):
        user = get_user_model().objects.create_superuser(
            email='testsuper@example.com',
            password='passme123',
        )
        assert user.is_superuser  == True
        assert user.is_staff  == True

    def test_create_recipe(self, create_user):
        # user = get_user_model().objects.create(
        #     email='tested@example.com',
        #     password='passme123'
        # )
        recipe = models.Recipe.objects.create(
            user=create_user,
            title='Sample recipe title',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample recipe description',
        )
        assert str(recipe) == recipe.title

    def test_create_tag(self, create_user):
        user = create_user
        tag = models.Tag.objects.create(user=user, name="Tag1")
        assert str(tag) == tag.name

    def test_create_ingredient(self, create_user):
        user = create_user
        ingredient = models.Ingredient.objects.create(user=user, name='Ingredient1')
        assert str(ingredient) == ingredient.name


