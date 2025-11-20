from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import MaterialProduccion
from innoquim.apps.lote_produccion.models import LoteProduccion
from innoquim.apps.materia_prima.models import MateriaPrima
from innoquim.apps.producto.models import Producto
from innoquim.apps.unidad.models import Unidad
from django.contrib.auth import get_user_model
from datetime import date

Usuario = get_user_model()


class MaterialProduccionModelTest(TestCase):
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
        self.materia_prima = MateriaPrima.objects.create(
            nombre="Materia Prima Test", codigo="MP001", unidad_id=self.unidad
        )
        self.lote = LoteProduccion.objects.create(
            product=self.producto,
            batch_code="LOTE001",
            production_date=date.today(),
            produced_quantity=100.00,
            unit=self.unidad,
            production_manager=self.user,
        )
        self.material = MaterialProduccion.objects.create(
            batch=self.lote,
            raw_material=self.materia_prima,
            used_quantity=20.00,
            unit=self.unidad,
        )

    def test_material_creation(self):
        self.assertEqual(self.material.used_quantity, 20.00)
        self.assertEqual(self.material.batch, self.lote)


class MaterialProduccionAPITest(APITestCase):
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
            nombre="Kilogramo", simbolo="kg", factor_conversion=1
        )
        self.producto = Producto.objects.create(
            product_code="PROD001", name="Producto Test", unit=self.unidad, weight=10.50
        )
        self.materia_prima = MateriaPrima.objects.create(
            nombre="Materia Prima Test", codigo="MP001", unidad_id=self.unidad
        )
        self.lote = LoteProduccion.objects.create(
            product=self.producto,
            batch_code="LOTE001",
            production_date=date.today(),
            produced_quantity=100.00,
            unit=self.unidad,
            production_manager=self.user,
        )

    def test_create_material(self):
        url = reverse("materialproduccion-list")
        data = {
            "batch": self.lote.id,
            "raw_material": self.materia_prima.materia_prima_id,
            "used_quantity": 15.00,
            "unit": self.unidad.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
