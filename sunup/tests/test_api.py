import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
def test_register_user():
    """Проверяем, что POST /api/auth/register/ создаёт пользователя"""
    client = APIClient()
    response = client.post("/api/auth/register/", {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "StrongPass123!",
        "password_confirm": "StrongPass123!",
    }, format="json")

    assert response.status_code == 201
    assert User.objects.filter(username="newuser").exists()