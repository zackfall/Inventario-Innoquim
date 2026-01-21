# Guía de Mejoras para Sistema de Inventario Puro

## Contexto Actual

Tu sistema está **muy bien implementado** para manejar inventario. Actualmente registras movimientos de entrada/salida con costos y mantenienes saldos actualizados. Nos enfocaremos solo en **gestión de inventario físico** sin presupuestos ni entregas.

---

## 🎯 Mejoras Críticas para Inventario (Prioridad Alta)

### 1. **Control de Lotes y Fechas de Vencimiento**

**¿Por qué lo necesitas?**
- Los productos químicos expiran y pierden efectividad
- Necesitas saber qué lote usar primero (FIFO)
- Trazabilidad para control de calidad

**¿Qué implementar?**

#### A. Modelo de Lotes
```python
class Lote(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    numero_lote = models.CharField(max_length=50, unique=True)
    fecha_fabricacion = models.DateField()
    fecha_vencimiento = models.DateField()
    cantidad_inicial = models.DecimalField(max_digits=10, decimal_places=3)
    cantidad_actual = models.DecimalField(max_digits=10, decimal_places=3)
    activo = models.BooleanField(default=True)
    
class Kardex(models.Model):
    # ... campos existentes ...
    lote = models.ForeignKey(Lote, null=True, blank=True, 
                             on_delete=models.SET_NULL)
```

#### B. Lógica FIFO Automática
```python
def obtener_lotes_disponibles(producto, almacen):
    """Retorna lotes disponibles ordenados por vencimiento"""
    return Lote.objects.filter(
        producto=producto,
        cantidad_actual__gt=0,
        activo=True
    ).order_by('fecha_vencimiento')

def registrar_salida_fifo(producto, cantidad, almacen):
    lotes = obtener_lotes_disponibles(producto, almacen)
    cantidad_restante = cantidad
    
    for lote in lotes:
        if cantidad_restante <= 0:
            break
            
        if lote.cantidad_actual >= cantidad_restante:
            # Usar todo de este lote
            cantidad_lote = cantidad_restante
            lote.cantidad_actual -= cantidad_restante
        else:
            # Usar todo el lote y seguir con el siguiente
            cantidad_lote = lote.cantidad_actual
            cantidad_restante -= lote.cantidad_actual
            lote.cantidad_actual = 0
            
        lote.save()
        
        # Registrar kardex para esta parte del lote
        Kardex.registrar_movimiento(
            producto=producto,
            almacen=almacen,
            tipo_movimiento='SALIDA',
            cantidad=cantidad_lote,
            lote=lote
        )
```

### 2. **Control de Stock Mínimo y Máximo**

**¿Para qué sirve?**
- Evitar desabastecimiento (stock mínimo)
- No sobrecargar almacén (stock máximo)
- Alertas automáticas de reorden

**Implementación:**
```python
class Producto(models.Model):
    # ... campos existentes ...
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=3, 
                                       default=0)
    stock_maximo = models.DecimalField(max_digits=10, decimal_places=3,
                                       default=0)
    punto_reorden = models.DecimalField(max_digits=10, decimal_places=3,
                                        default=0)
    
    @property
    def necesita_reorden(self):
        stock_actual = Kardex.obtener_saldo_actual(self)
        return stock_actual <= self.punto_reorden
    
    @property
    def stock_bajo(self):
        stock_actual = Kardex.obtener_saldo_actual(self)
        return stock_actual <= self.stock_minimo

# Señal para alertas automáticas
@receiver(post_save, sender=Kardex)
def verificar_stock(sender, instance, created, **kwargs):
    if created and instance.tipo_movimiento == 'SALIDA':
        producto = instance.content_object
        if hasattr(producto, 'stock_bajo') and producto.stock_bajo:
            # Enviar notificación
            enviar_alerta_stock_bajo(producto)
```

### 3. **Ubicaciones de Almacén Detalladas**

**¿Por qué es importante?**
- Saber exactamente dónde está cada producto
- Optimizar espacio de almacenamiento
- Facilitar picking y conteo físico

**Modelo Mejorado:**
```python
class Ubicacion(models.Model):
    almacen = models.ForeignKey('Almacen', on_delete=models.CASCADE)
    pasillo = models.CharField(max_length=10)
    estante = models.CharField(max_length=10)
    nivel = models.CharField(max_length=10)
    posicion = models.CharField(max_length=10)
    activa = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['almacen', 'pasillo', 'estante', 'nivel', 'posicion']
    
    def __str__(self):
        return f"{self.almacen.nombre} - P{self.pasillo}E{self.estante}N{self.nivel}P{self.posicion}"

class StockUbicacion(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    ubicacion = models.ForeignKey('Ubicacion', on_delete=models.CASCADE)
    lote = models.ForeignKey('Lote', null=True, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=3)
    
    class Meta:
        unique_together = ['producto', 'ubicacion', 'lote']
```

---

## 🔧 Mejoras Operativas (Prioridad Media)

### 4. **Ajustes de Inventario**

**¿Por qué necesitas ajustes?**
- Diferencias entre kardex y conteo físico
- Pérdidas por roturas o vencimiento
- Correcciones de errores de registro

**Tipos de Ajustes:**
```python
class AjusteInventario(models.Model):
    TIPO_CHOICES = [
        ('MERMA', 'Merma/Pérdida'),
        ('SOBRANTE', 'Sobrante'),
        ('CORRECCION', 'Corrección de Error'),
        ('VENCIDO', 'Producto Vencido'),
    ]
    
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    almacen = models.ForeignKey('Almacen', on_delete=models.CASCADE)
    tipo_ajuste = models.CharField(max_length=20, choices=TIPO_CHOICES)
    cantidad_anterior = models.DecimalField(max_digits=10, decimal_places=3)
    cantidad_nueva = models.DecimalField(max_digits=10, decimal_places=3)
    diferencia = models.DecimalField(max_digits=10, decimal_places=3)
    motivo = models.TextField()
    usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        self.diferencia = self.cantidad_nueva - self.cantidad_anterior
        
        # Registrar movimiento kardex automático
        if self.diferencia != 0:
            Kardex.registrar_movimiento(
                producto=self.producto,
                almacen=self.almacen,
                tipo_movimiento='SALIDA' if self.diferencia < 0 else 'ENTRADA',
                cantidad=abs(self.diferencia),
                motivo='AJUSTE',
                observaciones=f"{self.tipo_ajuste}: {self.motivo}"
            )
        
        super().save(*args, **kwargs)
```

### 5. **Transferencias entre Almacenes**

**¿Cuándo necesitas transferencias?**
- Mover producto entre bodegas
- Reorganización de inventario
- Prestamos entre departamentos

**Implementación:**
```python
class Transferencia(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_TRANSITO', 'En Tránsito'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    almacen_origen = models.ForeignKey('Almacen', on_delete=models.CASCADE, 
                                      related_name='transferencias_salida')
    almacen_destino = models.ForeignKey('Almacen', on_delete=models.CASCADE,
                                       related_name='transferencias_entrada')
    cantidad = models.DecimalField(max_digits=10, decimal_places=3)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, 
                             default='PENDIENTE')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    solicitante = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    observaciones = models.TextField(blank=True)
    
    def procesar_transferencia(self):
        """Ejecuta el movimiento físico entre almacenes"""
        if self.estado != 'PENDIENTE':
            raise ValidationError("Solo se pueden procesar transferencias pendientes")
        
        # Salida del almacén origen
        Kardex.registrar_movimiento(
            producto=self.producto,
            almacen=self.almacen_origen,
            tipo_movimiento='SALIDA',
            cantidad=self.cantidad,
            motivo='TRANSFERENCIA',
            referencia_id=self.id
        )
        
        # Entrada al almacén destino
        Kardex.registrar_movimiento(
            producto=self.producto,
            almacen=self.almacen_destino,
            tipo_movimiento='ENTRADA',
            cantidad=self.cantidad,
            motivo='TRANSFERENCIA',
            referencia_id=self.id
        )
        
        self.estado = 'COMPLETADA'
        self.fecha_completado = timezone.now()
        self.save()
```

---

## 📊 Mejoras de Consulta y Reportes (Prioridad Baja)

### 6. **Dashboard de Inventario**

**Métricas Clave:**
- Stock total por producto
- Valor del inventario
- Productos con bajo stock
- Próximos a vencer
- Movimientos del día

### 7. **Reportes Esenciales**

**Reportes Necesarios:**
```python
# 1. Reporte de Existencias Actuales
def reporte_existencias():
    return Kardex.objects.filter(
        # Último movimiento de cada producto
    ).values('producto', 'almacen', 'saldo_cantidad', 'saldo_costo_total')

# 2. Reporte de Productos por Vencer
def reporte_vencimiento(dias=30):
    limite = timezone.now() + timedelta(days=dias)
    return Lote.objects.filter(
        fecha_vencimiento__lte=limite,
        cantidad_actual__gt=0
    ).order_by('fecha_vencimiento')

# 3. Kardex Completo de Producto
def kardex_producto(producto, almacen, fecha_inicio, fecha_fin):
    return Kardex.objects.filter(
        content_type=ContentType.objects.get_for_model(producto),
        object_id=producto.id,
        almacen=almacen,
        fecha__range=[fecha_inicio, fecha_fin]
    ).order_by('fecha')
```

---

## 🚀 Plan de Implementación Simplificado

### Fase 1 (1-2 semanas) - Lo Básico
1. ✅ Crear modelo `Lote`
2. ✅ Agregar fecha de vencimiento y fabricación
3. ✅ Modificar `Kardex` para relacionar con lotes
4. ✅ Implementar lógica FIFO básica

### Fase 2 (1-2 semanas) - Control de Stock
1. ✅ Agregar campos de stock mínimo/máximo a `Producto`
2. ✅ Implementar alertas automáticas
3. ✅ Crear sistema de ajustes de inventario
4. ✅ Transferencias entre almacenes

### Fase 3 (1-2 semanas) - Operación
1. ✅ Mejorar ubicaciones detalladas
2. ✅ Dashboard básico de inventario
3. ✅ Reportes esenciales
4. ✅ Testing y validación

---

## 💡 Ejemplos Prácticos de Uso

### Escenario 1: Recepción de Producto con Lote
```python
# Recibir 100 unidades del producto "Cloruro de Sodio"
producto = Producto.objects.get(nombre="Cloruro de Sodio")
almacen = Almacen.objects.get(nombre="Bodega Principal")

# Crear lote
lote = Lote.objects.create(
    producto=producto,
    numero_lote="CLORO2024-001",
    fecha_fabricacion="2024-01-01",
    fecha_vencimiento="2025-12-31",
    cantidad_inicial=100,
    cantidad_actual=100
)

# Registrar entrada
Kardex.registrar_movimiento(
    producto=producto,
    almacen=almacen,
    tipo_movimiento='ENTRADA',
    cantidad=100,
    costo_unitario=15.50,
    lote=lote,
    motivo='COMPRA'
)
```

### Escenario 2: Salida con FIFO Automático
```python
# Consumir 30 unidades para producción
producto = Producto.objects.get(nombre="Cloruro de Sodio")
almacen = Almacen.objects.get(nombre="Bodega Principal")

# El sistema automáticamente:
# 1. Busca lotes disponibles ordenados por vencimiento
# 2. Usa el lote más antiguo primero
# 3. Actualiza cantidades del lote
# 4. Registra kardex correspondiente
registrar_salida_fifo(producto, 30, almacen)
```

### Escenario 3: Alerta de Stock Bajo
```python
# Si el producto tiene stock mínimo de 50 unidades
# Después de la salida anterior, quedan 70 unidades
# El sistema verifica si 70 <= 50 (no hay alerta todavía)

# Pero si se consumen 25 unidades más:
registrar_salida_fifo(producto, 25, almacen)  # Quedan 45 unidades
# ✅ SISTEMA ENVÍA ALERTA AUTOMÁTICA
# "¡Alerta! Cloruro de Sodio está por debajo del stock mínimo (45 < 50)"
```

---

## ⚠️ Validaciones Importantes

### No Permitir:
1. **Stock negativo** en cualquier momento
2. **Vencimiento pasado** al registrar entrada
3. **Transferencias sin stock** suficiente
4. **Lotes duplicados** para mismo producto

### Validar Siempre:
1. **Fechas de vencimiento** > fecha fabricación
2. **Cantidades positivas** en movimientos
3. **Stock disponible** antes de salidas
4. **Costos válidos** (mayores a cero)

---

## 🎯 Próximos Pasos Inmediatos

1. **Revisar tu inventario actual** - ¿Tienes productos con vencimiento?
2. **Decidir si necesitas lotes** - ¿Tienes productos de diferentes fabricantes?
3. **Evaluar tu espacio** - ¿Necesitas control detallado de ubicaciones?
4. **Definir stocks mínimos** - ¿Cuánto stock de seguridad necesitas?

---

## 📞 Soporte Continuo

Esta guía se enfoca **100% en inventario físico**. Si tienes dudas sobre:
- Cómo implementar lotes para tus productos específicos
- Qué validaciones necesitas para tu tipo de químicos
- Cómo configurar alertas útiles para tu operación
- Cómo organizar tus almacenes eficientemente

¡Pregunta随时! El objetivo es tener un inventario **robusto, confiable y fácil de gestionar**.

---

*Ultima actualización: Enero 2026*  
*Enfocado en gestión de inventario físico puro*