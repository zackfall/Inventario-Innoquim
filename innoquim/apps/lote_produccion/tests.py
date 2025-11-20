from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import LoteProduccion
from innoquim.apps.producto.models import Producto
from innoquim.apps.unidad.models import Unidad
from django.contrib.auth import get_user_model
from datetime import date

Usuario = get_user_model()


class LoteProduccionModelTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            email="manager@test.com",
            username="manager",
            name="Manager",
            password="pass123",
        )
        self.unidad = Unidad.objects.create(
            nombre="Kilogramo", simbolo="kg", factor_conversion=1
        )

        self.producto = Producto.objects.create(
            product_code="PROD001", name="Producto Test", unit=self.unidad, weight=10.50
        )
        self.lote = LoteProduccion.objects.create(
            product=self.producto,
            batch_code="LOTE001",
            production_date=date.today(),
            produced_quantity=100.00,
            unit=self.unidad,
            production_manager=self.user,
        )

    def test_lote_creation(self):
        self.assertEqual(self.lote.batch_code, "LOTE001")
        self.assertEqual(self.lote.status, "pending")


class LoteProduccionAPITest(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            email="test@example.com",
            username="testuser",
            name="Test User",
            password="testpass123",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)
        self.unidad = Unidad.objects.create(name="Kilogramo", abbreviation="kg")
        self.producto = Producto.objects.create(
            product_code="PROD001", name="Producto Test", unit=self.unidad, weight=10.50
        )

    def test_create_lote(self):
        url = reverse("loteproduccion-list")
        data = {
            "product": self.producto.id,
            "batch_code": "LOTE002",
            "production_date": date.today().isoformat(),
            "produced_quantity": 50.00,
            "unit": self.unidad.id,
            "production_manager": self.user.id,
            "status": "pending",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
