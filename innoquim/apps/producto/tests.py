from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Producto
from innoquim.apps.unidad.models import Unidad
from django.contrib.auth import get_user_model

Usuario = get_user_model()


class ProductoModelTest(TestCase):
    def setUp(self):
        self.unidad = Unidad.objects.create(
            nombre="Kilogramo", simbolo="kg", factor_conversion=1.0
        )
        self.producto = Producto.objects.create(
            product_code="PROD001",
            name="Producto Test",
            description="Descripción test",
            unit=self.unidad,
            weight=10.50,
        )

    def test_producto_creation(self):
        self.assertEqual(self.producto.product_code, "PROD001")
        self.assertEqual(self.producto.name, "Producto Test")

    def test_producto_str(self):
        self.assertEqual(str(self.producto), "PROD001 - Producto Test")


class ProductoAPITest(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            email="test@example.com",
            username="testuser",
            name="Test User",
            password="testpass123",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)
        self.unidad = Unidad.objects.create(
            nombre="Kilogramo", simbolo="kg", factor_conversion=1.0
        )

    def test_create_producto(self):
        url = reverse("producto-list")
        data = {
            "product_code": "PROD002",
            "name": "Nuevo Producto",
            "description": "Descripción nueva",
            "unit": self.unidad.id,
            "weight": 20.00,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Producto.objects.count(), 1)

    def test_list_productos(self):
        Producto.objects.create(
            product_code="PROD001", name="Producto Test", unit=self.unidad, weight=10.50
        )
        url = reverse("producto-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
