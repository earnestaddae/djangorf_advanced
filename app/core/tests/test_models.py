import pytest

from django.contrib.auth import get_user_model


pytestmark = pytest.mark.django_db


class TestModel:

    def test_create_user_with_email_successful(self):
        email = 'testme@example.com'
        password = 'passme123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )
        assert user.email == email
        assert user.check_password(password) == True

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


