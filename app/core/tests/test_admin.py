import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse


pytestmark = pytest.mark.django_db

@pytest.fixture
def admin_and_user(client):
    admin_user = get_user_model().objects.create_superuser(
        email='admin@example.com',
        password='passadmin',
    )
    client.force_login(admin_user)
    user = get_user_model().objects.create_user(
        email='user@example.com',
        password='passuser',
        name='userme',
    )
    return admin_user, user

class TestAdminSite:

    def test_users_list(self, admin_and_user, client):
        url = reverse('admin:core_user_changelist')
        res = client.get(url)
        _, user = admin_and_user
        assert res.status_code == 200
        assert user.name in str(res.content)
        assert user.email in str(res.content)

    def test_edit_user_page(self, admin_and_user, client):
        _, user = admin_and_user
        url = reverse('admin:core_user_change', args=[user.id])
        res = client.get(url)
        assert res.status_code == 200

    def test_create_user_page(self, admin_and_user, client):
        url = reverse('admin:core_user_add')
        res = client.get(url)
        assert res.status_code == 200