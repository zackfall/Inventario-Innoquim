from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from innoquim.apps.usuario.models import Usuario
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock

from innoquim.apps.almacen.models import Almacen
from innoquim.apps.materia_prima.models import MateriaPrima
from innoquim.apps.unidad.models import Unidad
from .models import RecepcionMaterial
from innoquim.apps.recepcion_item.models import RecepcionItem
from innoquim.apps.inventario.models import Kardex
from innoquim.apps.inventario_material.models import InventarioMaterial


class RecepcionMaterialModelTest(TestCase):
    """Tests para el modelo RecepcionMaterial"""
    
    def setUp(self):
        self.unidad = Unidad.objects.create(
            nombre="KG", 
            simbolo="kg",
            factor_conversion=1.0
        )
        self.almacen = Almacen.objects.create(nombre="Almacén Principal", direccion="Planta 1")
        self.materia_prima = MateriaPrima.objects.create(
            nombre="Ácido Sulfúrico",
            codigo="AC-SUL-98",
            unidad_id=self.unidad
        )
        
    def test_creacion_recepcion_material(self):
        """Test crear RecepcionMaterial correctamente"""
        recepcion = RecepcionMaterial.objects.create(
            materia_prima=self.materia_prima,
            cantidad=Decimal("100.50"),
            costo_unitario=Decimal("25.75"),
            proveedor="Químicos del Norte",
            almacen=self.almacen,
            fecha_de_recepcion="2026-01-20",
            numero_de_factura="FAC-2026-001",
            observaciones="Recepción de prueba"
        )
        
        self.assertEqual(recepcion.materia_prima, self.materia_prima)
        self.assertEqual(recepcion.cantidad, Decimal("100.50"))
        self.assertEqual(recepcion.costo_unitario, Decimal("25.75"))
        self.assertEqual(recepcion.total, Decimal("2587.8750"))  # 100.50 * 25.75
        self.assertEqual(recepcion.proveedor, "Químicos del Norte")
        self.assertEqual(recepcion.almacen, self.almacen)
        
    def test_calculo_automatico_total(self):
        """Test que el total se calcule automáticamente"""
        recepcion = RecepcionMaterial(
            materia_prima=self.materia_prima,
            cantidad=Decimal("50"),
            costo_unitario=Decimal("10"),
            proveedor="Proveedor Test",
            almacen=self.almacen,
            fecha_de_recepcion="2026-01-20"
        )
        recepcion.save()
        
        self.assertEqual(recepcion.total, Decimal("500"))
        
    def test_str_representacion(self):
        """Test representación string del modelo"""
        recepcion = RecepcionMaterial.objects.create(
            materia_prima=self.materia_prima,
            cantidad=Decimal("10"),
            costo_unitario=Decimal("5"),
            proveedor="Test",
            almacen=self.almacen,
            fecha_de_recepcion="2026-01-20"
        )
        
        expected = f"Recepción {recepcion.id} - Ácido Sulfúrico (2026-01-20)"
        self.assertEqual(str(recepcion), expected)
        
    def test_campos_opcionales(self):
        """Test que los campos opcionales puedan ser nulos"""
        recepcion = RecepcionMaterial.objects.create(
            materia_prima=self.materia_prima,
            cantidad=Decimal("10"),
            costo_unitario=Decimal("5"),
            proveedor="Test",
            almacen=self.almacen,
            fecha_de_recepcion="2026-01-20"
            # Sin observaciones ni numero_de_factura
        )
        
        self.assertIsNone(recepcion.observaciones)
        self.assertIsNone(recepcion.numero_de_factura)


class RecepcionItemModelTest(TestCase):
    """Tests para el modelo RecepcionItem"""
    
    def setUp(self):
        self.unidad = Unidad.objects.create(
            nombre="KG", 
            simbolo="kg",
            factor_conversion=1.0
        )
        self.almacen = Almacen.objects.create(nombre="Almacén Principal", direccion="Planta 1")
        self.materia_prima = MateriaPrima.objects.create(
            nombre="Hidróxido de Sodio",
            codigo="HID-SOD-99",
            unidad_id=self.unidad
        )
        self.recepcion = RecepcionMaterial.objects.create(
            materia_prima=self.materia_prima,
            cantidad=Decimal("100"),
            costo_unitario=Decimal("15"),
            proveedor="Test Proveedor",
            almacen=self.almacen,
            fecha_de_recepcion="2026-01-20"
        )
        
    def test_creacion_recepcion_item(self):
        """Test crear RecepcionItem correctamente"""
        item = RecepcionItem.objects.create(
            id_recepcion_material=self.recepcion,
            materia_prima=self.materia_prima,
            cantidad=50,
            id_unidad=self.unidad,
            lote="LOT-001",
            precio_compra=Decimal("12.50"),
            observaciones="Item de prueba"
        )
        
        self.assertEqual(item.id_recepcion_material, self.recepcion)
        self.assertEqual(item.materia_prima, self.materia_prima)
        self.assertEqual(item.cantidad, 50)
        self.assertEqual(item.id_unidad, self.unidad)
        self.assertEqual(item.lote, "LOT-001")
        self.assertEqual(item.precio_compra, Decimal("12.50"))


class KardexIntegrationTest(TestCase):
    """Tests para la integración con Kardex"""
    
    def setUp(self):
        self.unidad = Unidad.objects.create(
            nombre="KG", 
            simbolo="kg",
            factor_conversion=1.0
        )
        self.almacen = Almacen.objects.create(nombre="Almacén Test", direccion="Test")
        self.materia_prima = MateriaPrima.objects.create(
            nombre="Cloruro de Sodio",
            codigo="CLOR-SOD-95",
            unidad_id=self.unidad
        )
        
    @patch('innoquim.apps.inventario.signals.actualizar_inventario_material')
    def test_signal_recepcion_material_crea_kardex(self, mock_actualizar):
        """Test que crear RecepcionMaterial genere movimiento en Kardex"""
        recepcion = RecepcionMaterial.objects.create(
            materia_prima=self.materia_prima,
            cantidad=Decimal("100"),
            costo_unitario=Decimal("20"),
            proveedor="Proveedor Test",
            almacen=self.almacen,
            fecha_de_recepcion="2026-01-20",
            numero_de_factura="FAC-001"
        )
        
        # Verificar que se creó el movimiento en Kardex
        kardex = Kardex.objects.filter(
            item=self.materia_prima,
            almacen=self.almacen,
            tipo_movimiento="ENTRADA",
            motivo="COMPRA"
        ).first()
        
        self.assertIsNotNone(kardex)
        self.assertEqual(kardex.cantidad, Decimal("100"))
        self.assertEqual(kardex.costo_unitario, Decimal("20"))
        self.assertEqual(kardex.referencia_id, f"RM{recepcion.id}-DIRECT")
        self.assertIn("Recepción directa", kardex.observaciones)
        self.assertIn("FAC-001", kardex.observaciones)
        self.assertIn("Proveedor Test", kardex.observaciones)
        
        # Verificar que se llamó a actualizar inventario
        mock_actualizar.assert_called_once_with(self.materia_prima, self.almacen)
        
    @patch('innoquim.apps.inventario.signals.actualizar_inventario_material')
    def test_signal_recepcion_item_crea_kardex(self, mock_actualizar):
        """Test que crear RecepcionItem genere movimiento en Kardex"""
        recepcion = RecepcionMaterial.objects.create(
            materia_prima=self.materia_prima,
            cantidad=Decimal("50"),
            costo_unitario=Decimal("15"),
            proveedor="Proveedor Test",
            almacen=self.almacen,
            fecha_de_recepcion="2026-01-20"
        )
        
        item = RecepcionItem.objects.create(
            id_recepcion_material=recepcion,
            materia_prima=self.materia_prima,
            cantidad=25,
            id_unidad=self.unidad,
            lote="LOT-002",
            precio_compra=Decimal("18.75")
        )
        
        # Verificar que se creó el movimiento en Kardex
        kardex = Kardex.objects.filter(
            item=self.materia_prima,
            almacen=self.almacen,
            tipo_movimiento="ENTRADA",
            motivo="COMPRA"
        ).first()
        
        self.assertIsNotNone(kardex)
        self.assertEqual(kardex.cantidad, Decimal("25"))
        self.assertEqual(kardex.costo_unitario, Decimal("18.75"))
        self.assertEqual(kardex.referencia_id, f"RM{recepcion.id}-ITEM{item.id}")
        self.assertIn("Recepción de material - Lote: LOT-002", kardex.observaciones)
        
        # Verificar que se llamó a actualizar inventario
        mock_actualizar.assert_called_once_with(self.materia_prima, self.almacen)


class RecepcionMaterialAPITest(APITestCase):
    """Tests para los endpoints de la API de RecepcionMaterial"""
    
    def setUp(self):
        self.user = Usuario.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.unidad = Unidad.objects.create(
            nombre="KG", 
            simbolo="kg",
            factor_conversion=1.0
        )
        self.almacen = Almacen.objects.create(nombre="Almacén API", direccion="Test")
        self.materia_prima = MateriaPrima.objects.create(
            nombre="Sulfato de Cobre",
            codigo="SUL-COP-98",
            unidad_id=self.unidad
        )
        
    def test_listar_recepciones(self):
        """Test listar todas las recepciones"""
        RecepcionMaterial.objects.create(
            materia_prima=self.materia_prima,
            cantidad=Decimal("10"),
            costo_unitario=Decimal("5"),
            proveedor="Test",
            almacen=self.almacen,
            fecha_de_recepcion="2026-01-20"
        )
        
        response = self.client.get('/api/recepciones/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
    def test_crear_recepcion(self):
        """Test crear una nueva recepción via API"""
        data = {
            'materia_prima': self.materia_prima.materia_prima_id,
            'cantidad': '100.50',
            'costo_unitario': '25.75',
            'proveedor': 'Proveedor API Test',
            'almacen': self.almacen.id,
            'fecha_de_recepcion': '2026-01-20',
            'numero_de_factura': 'FAC-API-001',
            'observaciones': 'Recepción via API'
        }
        
        response = self.client.post('/api/recepciones/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        recepcion = RecepcionMaterial.objects.get(id=response.data['id'])
        self.assertEqual(recepcion.proveedor, 'Proveedor API Test')
        self.assertEqual(recepcion.total, Decimal('2587.8750'))  # Calculado automáticamente
        
    def test_filtrar_por_almacen(self):
        """Test filtrar recepciones por almacén"""
        almacen2 = Almacen.objects.create(nombre="Almacén 2", direccion="Otro")
        
        RecepcionMaterial.objects.create(
            materia_prima=self.materia_prima,
            cantidad=Decimal("10"),
            costo_unitario=Decimal("5"),
            proveedor="Test",
            almacen=self.almacen,
            fecha_de_recepcion="2026-01-20"
        )
        
        RecepcionMaterial.objects.create(
            materia_prima=self.materia_prima,
            cantidad=Decimal("15"),
            costo_unitario=Decimal("7"),
            proveedor="Test",
            almacen=almacen2,
            fecha_de_recepcion="2026-01-20"
        )
        
        # Filtrar por primer almacén
        response = self.client.get(f'/api/recepciones/?almacen={self.almacen.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['almacen'], self.almacen.id)
        
    def test_buscar_por_proveedor(self):
        """Test búsqueda por proveedor"""
        RecepcionMaterial.objects.create(
            materia_prima=self.materia_prima,
            cantidad=Decimal("10"),
            costo_unitario=Decimal("5"),
            proveedor="Químicos del Norte",
            almacen=self.almacen,
            fecha_de_recepcion="2026-01-20"
        )
        
        RecepcionMaterial.objects.create(
            materia_prima=self.materia_prima,
            cantidad=Decimal("15"),
            costo_unitario=Decimal("7"),
            proveedor="Industrias del Sur",
            almacen=self.almacen,
            fecha_de_recepcion="2026-01-20"
        )
        
        response = self.client.get('/api/recepciones/?search=Químicos')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['proveedor'], 'Químicos del Norte')
        
    def test_validacion_cantidad_costo(self):
        """Test validación de campos numéricos"""
        data = {
            'materia_prima': self.materia_prima.materia_prima_id,
            'cantidad': '-10',  # Cantidad negativa no debería ser válida
            'costo_unitario': '5',
            'proveedor': 'Test',
            'almacen': self.almacen.id,
            'fecha_de_recepcion': '2026-01-20'
        }
        
        response = self.client.post('/api/recepciones/', data)
        # Django DecimalField no permite negativos por default, pero si fuera necesario
        # se debería agregar validación personalizada
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RecepcionMaterialSerializerTest(TestCase):
    """Tests para el serializer de RecepcionMaterial"""
    
    def setUp(self):
        self.unidad = Unidad.objects.create(
            nombre="KG", 
            simbolo="kg",
            factor_conversion=1.0
        )
        self.almacen = Almacen.objects.create(nombre="Almacén Serializer", direccion="Test")
        self.materia_prima = MateriaPrima.objects.create(
            nombre="Nitrato de Potasio",
            codigo="NIT-POT-99",
            unidad_id=self.unidad
        )
        
    def test_serializer_valido(self):
        """Test serializer con datos válidos"""
        from .serializers import RecepcionMaterialSerializer
        
        data = {
            'materia_prima': self.materia_prima.materia_prima_id,
            'cantidad': '100.50',
            'costo_unitario': '25.75',
            'proveedor': 'Proveedor Serializer',
            'almacen': self.almacen.id,
            'fecha_de_recepcion': '2026-01-20',
            'numero_de_factura': 'FAC-SER-001'
        }
        
        serializer = RecepcionMaterialSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        # Verificar cálculo automático del total
        validated_data = serializer.save()
        self.assertEqual(validated_data.total, Decimal('2587.8750'))
        
    def test_campo_total_formateado(self):
        """Test campo calculado total_formateado"""
        from .serializers import RecepcionMaterialSerializer
        
        recepcion = RecepcionMaterial.objects.create(
            materia_prima=self.materia_prima,
            cantidad=Decimal("100"),
            costo_unitario=Decimal("10.50"),
            proveedor="Test",
            almacen=self.almacen,
            fecha_de_recepcion="2026-01-20"
        )
        
        serializer = RecepcionMaterialSerializer(recepcion)
        self.assertEqual(serializer.data['total_formateado'], '$1,050.00')
        
    def test_campos_relacionados(self):
        """Test que incluya datos de relaciones"""
        from .serializers import RecepcionMaterialSerializer
        
        recepcion = RecepcionMaterial.objects.create(
            materia_prima=self.materia_prima,
            cantidad=Decimal("50"),
            costo_unitario=Decimal("15"),
            proveedor="Test",
            almacen=self.almacen,
            fecha_de_recepcion="2026-01-20"
        )
        
        serializer = RecepcionMaterialSerializer(recepcion)
        
        # Verificar que incluye detalles de relaciones
        self.assertIn('almacen_detail', serializer.data)
        self.assertIn('materia_prima_detail', serializer.data)
        self.assertEqual(serializer.data['almacen_detail']['nombre'], 'Almacén Serializer')
        self.assertEqual(serializer.data['materia_prima_detail']['nombre'], 'Nitrato de Potasio')