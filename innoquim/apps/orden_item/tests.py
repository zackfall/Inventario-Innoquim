from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import OrdenItem
from innoquim.apps.orden_cliente.models import OrdenCliente
from innoquim.apps.cliente.models import Cliente
from innoquim.apps.producto.models import Producto
from innoquim.apps.unidad.models import Unidad
from django.contrib.auth import get_user_model
from datetime import date

Usuario = get_user_model()


class OrdenItemModelTest(TestCase):
    def setUp(self):
        self.unidad = Unidad.objects.create(
            nombre="Kilogramo", simbolo="kg", factor_conversion=1
        )

        self.producto = Producto.objects.create(
            product_code="PROD001", name="Producto Test", unit=self.unidad, weight=10.50
        )
        self.cliente = Cliente.objects.create(
            nombre_empresa="Empresa Test",
            ruc="1234567890123",
            email="cliente@test.com",
            direccion="Direccion Test",
        )
        self.orden = OrdenCliente.objects.create(
            client=self.cliente, order_code="ORD001", order_date=date.today()
        )
        self.orden_item = OrdenItem.objects.create(
            order=self.orden, product=self.producto, quantity=5.00, unit=self.unidad
        )

    def test_orden_item_creation(self):
        self.assertEqual(self.orden_item.quantity, 5.00)
        self.assertEqual(self.orden_item.product, self.producto)


class OrdenItemAPITest(APITestCase):
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
        self.cliente = Cliente.objects.create(
            nombre_empresa="Empresa Test",
            ruc="1234567890123",
            email="cliente@test.com",
            direccion="Direccion Test",
        )
        self.orden = OrdenCliente.objects.create(
            client=self.cliente, order_code="ORD001", order_date=date.today()
        )

    def test_create_orden_item(self):
        url = reverse("ordenitem-list")
        data = {
            "order": self.orden.id,
            "product": self.producto.id,
            "quantity": 10.00,
            "unit": self.unidad.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
