# 📋 Documentación de API: Lotes de Producción

## 🎯 Resumen

Este documento describe los endpoints implementados en el backend Django para la gestión de **Lotes de Producción** y **Materiales de Producción**.

---

## 📚 Endpoints Principales

### Base URL
```
http://localhost:8000/api/v1
```

---

## 🏭 Lotes de Producción

### 1. Listar Lotes de Producción

**GET** `/lotes-produccion/`

**Query Parameters:**
- `search`: Buscar por código de lote o nombre de producto
  - Ejemplo: `?search=LP001`
- `status`: Filtrar por estado (pending, in_progress, completed, cancelled)
  - Ejemplo: `?status=completed`
- `product`: Filtrar por ID de producto
  - Ejemplo: `?product=1`
- `production_manager`: Filtrar por ID del gestor
  - Ejemplo: `?production_manager=1`
- `page`: Número de página (paginación)
  - Ejemplo: `?page=2`
- `ordering`: Ordenar resultados (default: `-production_date`)
  - Ejemplo: `?ordering=batch_code`

**Ejemplo:**
```bash
curl -X GET http://localhost:8000/api/v1/lotes-produccion/?status=completed
```

**Respuesta (200):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "product": 1,
      "product_name": "Shampoo",
      "product_code": "PROD-001",
      "batch_code": "LP001-2025",
      "production_date": "2025-01-15",
      "produced_quantity": "50.00",
      "unit": 1,
      "unit_name": "Kilogramo",
      "unit_symbol": "kg",
      "status": "completed",
      "production_manager": 1,
      "production_manager_name": "Juan García",
      "materiales": [
        {
          "id": 1,
          "batch": 1,
          "batch_code": "LP001-2025",
          "raw_material": 1,
          "raw_material_name": "Sal",
          "raw_material_codigo": "MP001",
          "raw_material_stock": "195.00",
          "raw_material_stock_minimo": "100.00",
          "raw_material_stock_maximo": "500.00",
          "used_quantity": "5.00",
          "unit": 1,
          "unit_name": "Kilogramo",
          "unit_symbol": "kg",
          "created_at": "2025-01-15T10:30:00Z",
          "updated_at": "2025-01-15T10:30:00Z"
        }
      ],
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-01-15T15:00:00Z"
    }
  ]
}
```

---

### 2. Obtener Detalles de un Lote

**GET** `/lotes-produccion/{id}/`

**Parámetros:**
- `id`: ID del lote (requerido)

**Ejemplo:**
```bash
curl -X GET http://localhost:8000/api/v1/lotes-produccion/1/
```

**Respuesta (200):** (mismo formato que arriba)

---

### 3. Crear Lote de Producción

**POST** `/lotes-produccion/`

**Headers:**
```
Content-Type: application/json
Authorization: Bearer {token}
```

**Body:**
```json
{
  "product": 1,
  "batch_code": "LP001-2025",
  "production_date": "2025-01-15",
  "produced_quantity": "50.00",
  "unit": 1,
  "status": "pending",
  "production_manager": 1
}
```

**Ejemplo:**
```bash
curl -X POST http://localhost:8000/api/v1/lotes-produccion/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 1,
    "batch_code": "LP001-2025",
    "production_date": "2025-01-15",
    "produced_quantity": "50.00",
    "unit": 1,
    "status": "pending",
    "production_manager": 1
  }'
```

**Respuesta (201):** (datos del lote creado)

**Errores:**
- `400 Bad Request`: Datos inválidos
- `401 Unauthorized`: Token inválido o no autenticado

---

### 4. Actualizar Lote

**PUT** `/lotes-produccion/{id}/`

**Body:** (igual al crear, actualiza todos los campos)
```json
{
  "product": 1,
  "batch_code": "LP001-2025",
  "production_date": "2025-01-15",
  "produced_quantity": "50.00",
  "unit": 1,
  "status": "in_progress",
  "production_manager": 1
}
```

**Ejemplo:**
```bash
curl -X PUT http://localhost:8000/api/v1/lotes-produccion/1/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'
```

**Respuesta (200):** (datos actualizados)

---

### 5. Cambiar Estado del Lote (PATCH)

**PATCH** `/lotes-produccion/{id}/`

**Body:** (actualiza solo los campos proporcionados)
```json
{
  "status": "completed"
}
```

**Ejemplo:**
```bash
curl -X PATCH http://localhost:8000/api/v1/lotes-produccion/1/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
```

**⚠️ IMPORTANTE:**
Cuando se cambia el status a `"completed"`:
- ✅ El stock del PRODUCTO aumenta en `produced_quantity`
- ✅ El stock de cada MATERIA PRIMA disminuye en `used_quantity`
- ✅ Se crean registros automáticos en el Kardex

**Respuesta (200):** (lote actualizado)

---

### 6. Eliminar Lote

**DELETE** `/lotes-produccion/{id}/`

**Ejemplo:**
```bash
curl -X DELETE http://localhost:8000/api/v1/lotes-produccion/1/ \
  -H "Authorization: Bearer {token}"
```

**Respuesta (204):** (sin contenido, éxito)

**Errores:**
- `404 Not Found`: Lote no existe

---

## 🧪 Materiales de Producción

### 1. Listar Materiales de un Lote

**GET** `/lotes-produccion/{id}/materiales/`

**Ejemplo:**
```bash
curl -X GET http://localhost:8000/api/v1/lotes-produccion/1/materiales/
```

**Respuesta (200):**
```json
[
  {
    "id": 1,
    "batch": 1,
    "batch_code": "LP001-2025",
    "raw_material": 1,
    "raw_material_name": "Sal",
    "raw_material_codigo": "MP001",
    "raw_material_stock": "195.00",
    "raw_material_stock_minimo": "100.00",
    "raw_material_stock_maximo": "500.00",
    "used_quantity": "5.00",
    "unit": 1,
    "unit_name": "Kilogramo",
    "unit_symbol": "kg",
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T10:30:00Z"
  }
]
```

---

### 2. Agregar Material a un Lote

**POST** `/lotes-produccion/{id}/materiales/`

**Body:**
```json
{
  "raw_material": 1,
  "used_quantity": "5.00",
  "unit": 1
}
```

**Ejemplo:**
```bash
curl -X POST http://localhost:8000/api/v1/lotes-produccion/1/materiales/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "raw_material": 1,
    "used_quantity": "5.00",
    "unit": 1
  }'
```

**Respuesta (201):** (material creado)

---

### 3. Obtener un Material Específico

**GET** `/lotes-produccion/{lote_id}/materiales/{material_id}/`

**Ejemplo:**
```bash
curl -X GET http://localhost:8000/api/v1/lotes-produccion/1/materiales/1/
```

**Respuesta (200):** (datos del material)

---

### 4. Actualizar Material

**PUT** `/lotes-produccion/{lote_id}/materiales/{material_id}/`

**Body:**
```json
{
  "raw_material": 1,
  "used_quantity": "10.00",
  "unit": 1
}
```

**Ejemplo:**
```bash
curl -X PUT http://localhost:8000/api/v1/lotes-produccion/1/materiales/1/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"used_quantity": "10.00"}'
```

**Respuesta (200):** (material actualizado)

---

### 5. Eliminar Material

**DELETE** `/lotes-produccion/{lote_id}/materiales/{material_id}/`

**Ejemplo:**
```bash
curl -X DELETE http://localhost:8000/api/v1/lotes-produccion/1/materiales/1/ \
  -H "Authorization: Bearer {token}"
```

**Respuesta (204):** (sin contenido, éxito)

---

## 📊 Materiales de Producción Globales

También puedes acceder a todos los materiales de producción sin especificar lote:

### 1. Listar Todos

**GET** `/materiales-produccion/`

**Query Parameters:**
- `batch`: Filtrar por ID de lote
- `raw_material`: Filtrar por ID de materia prima
- `search`: Buscar por nombre o código

**Ejemplo:**
```bash
curl -X GET http://localhost:8000/api/v1/materiales-produccion/?batch=1
```

---

### 2. Crear Material (directamente)

**POST** `/materiales-produccion/`

```bash
curl -X POST http://localhost:8000/api/v1/materiales-produccion/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "batch": 1,
    "raw_material": 1,
    "used_quantity": "5.00",
    "unit": 1
  }'
```

---

### 3. Actualizar Material

**PUT** `/materiales-produccion/{id}/`

```bash
curl -X PUT http://localhost:8000/api/v1/materiales-produccion/1/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"used_quantity": "10.00"}'
```

---

### 4. Eliminar Material

**DELETE** `/materiales-produccion/{id}/`

```bash
curl -X DELETE http://localhost:8000/api/v1/materiales-produccion/1/ \
  -H "Authorization: Bearer {token}"
```

---

## 🔄 Flujo Completo: Crear un Lote con Materiales

```bash
# 1. Crear el lote
curl -X POST http://localhost:8000/api/v1/lotes-produccion/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 1,
    "batch_code": "LP001-2025",
    "production_date": "2025-01-15",
    "produced_quantity": "50.00",
    "unit": 1,
    "status": "pending",
    "production_manager": 1
  }'
# Respuesta: {"id": 1, ...}

# 2. Agregar primer material
curl -X POST http://localhost:8000/api/v1/lotes-produccion/1/materiales/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "raw_material": 1,
    "used_quantity": "5.00",
    "unit": 1
  }'

# 3. Agregar segundo material
curl -X POST http://localhost:8000/api/v1/lotes-produccion/1/materiales/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "raw_material": 2,
    "used_quantity": "10.00",
    "unit": 1
  }'

# 4. Cambiar a "en proceso"
curl -X PATCH http://localhost:8000/api/v1/lotes-produccion/1/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'

# 5. Completar el lote (↑ stock producto, ↓ stock materiales)
curl -X PATCH http://localhost:8000/api/v1/lotes-produccion/1/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
```

---

## 📝 Campos Disponibles

### LoteProduccion

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | Integer | Auto | ID único del lote |
| `product` | Integer (FK) | ✅ | ID del producto a producir |
| `batch_code` | String(50) | ✅ | Código único del lote |
| `production_date` | Date | ✅ | Fecha de producción |
| `produced_quantity` | Decimal | ✅ | Cantidad producida |
| `unit` | Integer (FK) | ✅ | ID de unidad de medida |
| `status` | Enum | ✅ | pending, in_progress, completed, cancelled |
| `production_manager` | Integer (FK) | ✅ | ID del usuario gestor |
| `created_at` | DateTime | Auto | Fecha de creación |
| `updated_at` | DateTime | Auto | Última actualización |

### MaterialProduccion

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | Integer | Auto | ID único |
| `batch` | Integer (FK) | ✅ | ID del lote |
| `raw_material` | Integer (FK) | ✅ | ID de materia prima |
| `used_quantity` | Decimal | ✅ | Cantidad utilizada |
| `unit` | Integer (FK) | ✅ | ID de unidad de medida |
| `created_at` | DateTime | Auto | Fecha de creación |
| `updated_at` | DateTime | Auto | Última actualización |

---

## ⚠️ Códigos de Estado HTTP

| Código | Significado |
|--------|-------------|
| `200 OK` | Solicitud exitosa |
| `201 Created` | Recurso creado |
| `204 No Content` | Eliminado exitosamente |
| `400 Bad Request` | Datos inválidos |
| `401 Unauthorized` | No autenticado |
| `403 Forbidden` | Sin permisos |
| `404 Not Found` | Recurso no existe |
| `500 Server Error` | Error del servidor |

---

## 🔐 Autenticación

Todos los endpoints requieren Bearer Token en el header:

```
Authorization: Bearer {access_token}
```

**Obtener Token:**
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario",
    "password": "contraseña"
  }'
```

---

## 💡 Notas Importantes

1. **Stock Automático**: Al completar un lote, los stocks se actualizan automáticamente
2. **Validaciones**: El backend valida que:
   - `batch_code` sea único
   - `produced_quantity` > 0
   - Los IDs de FK existan
3. **Kardex**: Se crean registros automáticos al completar lotes
4. **Permisos**: Requiere autenticación (JWT Token)

---

**Última actualización**: Enero 2025
**Versión API**: v1
