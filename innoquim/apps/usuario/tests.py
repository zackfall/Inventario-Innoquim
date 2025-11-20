from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

Usuario = get_user_model()


class UsuarioModelTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            email="test@example.com",
            username="testuser",
            name="Test User",
            password="testpass123",
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, "test@example.com")
        self.assertEqual(self.user.username, "testuser")
        self.assertTrue(self.user.check_password("testpass123"))

    def test_user_str(self):
        self.assertEqual(str(self.user), "Test User (test@example.com)")


class UsuarioAPITest(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            email="test@example.com",
            username="testuser",
            name="Test User",
            password="testpass123",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_create_usuario(self):
        url = reverse("usuario-list")
        data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "name": "New User",
            "password": "newpass123",
            "rol": "employee",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Usuario.objects.count(), 2)

    def test_list_usuarios(self):
        url = reverse("usuario-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
