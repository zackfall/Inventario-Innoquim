# Sistema de Gestión CEISH - Innoquim

Sistema de gestión integral para control de inventarios, producción y órdenes de cliente desarrollado con Django REST Framework.

## 📋 Características

- **Gestión de Usuarios**: Sistema de autenticación con roles personalizados (admin, manager, employee, client)
- **Gestión de Productos**: Control completo de productos con códigos, descripciones y unidades
- **Gestión de Clientes**: Administración de clientes con información fiscal
- **Órdenes de Cliente**: Seguimiento de órdenes con múltiples items
- **Gestión de Materias Primas**: Control de materiales para producción
- **Lotes de Producción**: Seguimiento de lotes con asignación de gerentes
- **Materiales de Producción**: Registro de materias primas usadas por lote
- **Pedidos de Material**: Sistema de pedidos a proveedores
- **Recepciones**: Control de calidad en recepciones de material
- **Inventario**: Control de stock con niveles mínimos y máximos
- **Almacenes**: Gestión de múltiples almacenes
- **Entregas**: Seguimiento de entregas a clientes
- **API RESTful**: API completa con documentación automática

## 🛠️ Tecnologías

- Python 3.12
- Django 5.2.7
- Django REST Framework 3.16.1
- PostgreSQL
- python-dotenv

## 📦 Requisitos Previos

- Python 3.12 o superior
- PostgreSQL instalado y funcionando
- pip (gestor de paquetes de Python)
- Git

## 🚀 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/zackfall/Inventario-Innoquim
cd Inventario-Innoquim
```

### 2. Configurar el Entorno Virtual (Recomendado)

#### Usando pyenv (Recomendado para Windows)

**Instalar pyenv:**
```powershell
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
```

**Verificar instalación:**
```powershell
pyenv --version
```

**Instalar Python 3.12:**
```powershell
pyenv install 3.12
pyenv global 3.12
```

**Verificar:**
```powershell
pyenv version
# Debería mostrar: 3.12 (set by \path\to\.pyenv\pyenv-win\.python-version)
```

#### Alternativa: Usando venv

```bash
# Linux/Mac
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos PostgreSQL

**Crear la base de datos:**

```sql
-- Conéctate a PostgreSQL
psql -U postgres

-- Crear la base de datos
CREATE DATABASE innoquim_db;

-- Crear usuario (opcional)
CREATE USER innoquim_user WITH PASSWORD 'tu_password_seguro';

-- Otorgar permisos
GRANT ALL PRIVILEGES ON DATABASE innoquim_db TO innoquim_user;

-- Salir
\q
```

### 5. Configurar Variables de Entorno

Copiar el archivo de ejemplo y configurarlo:

```bash
cp .env.example .env
```

Editar el archivo `.env` con tus configuraciones:

```env
# Generar SECRET_KEY (ver instrucciones abajo)
SECRET_KEY="tu_secret_key_generada"

# Modo desarrollo
DEBUG=True

# Configuración de PostgreSQL
NAME="innoquim_db"
USER="postgres"  # o "innoquim_user"
PASSWORD="tu_password"
HOST="localhost"
PORT="5432"
```

**Generar SECRET_KEY:**

```bash
python
```

```python
import secrets
secret_key = secrets.token_urlsafe(64)
print(secret_key)
exit()
```

Copia el resultado y pégalo en `SECRET_KEY` en el archivo `.env`.

### 6. Crear y Aplicar Migraciones

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate
```

### 7. Crear Superusuario

```bash
python manage.py createsuperuser
```

Se te pedirá:
- **Email**: admin@example.com
- **Username**: admin
- **Name**: Administrador
- **Password**: (tu contraseña segura)

### 8. Ejecutar el Servidor

```bash
python manage.py runserver
```

El servidor estará disponible en: `http://localhost:8000`

## 🔗 Endpoints de la API

### Panel de Administración
- **Admin**: http://localhost:8000/admin/

### API REST
- **API Root**: http://localhost:8000/api/
- **API Authentication**: http://localhost:8000/api-auth/

### Recursos Disponibles

| Recurso | Endpoint | Descripción |
|---------|----------|-------------|
| Usuarios | `/api/usuarios/` | Gestión de usuarios |
| Unidades | `/api/unidades/` | Unidades de medida |
| Productos | `/api/productos/` | Catálogo de productos |
| Clientes | `/api/clientes/` | Gestión de clientes |
| Órdenes Cliente | `/api/ordenes-cliente/` | Órdenes de clientes |
| Orden Items | `/api/orden-items/` | Items de órdenes |
| Materias Primas | `/api/materias-primas/` | Catálogo de materias primas |
| Lotes Producción | `/api/lotes-produccion/` | Control de lotes |
| Materiales Producción | `/api/materiales-produccion/` | Materiales por lote |
| Pedidos Material | `/api/pedidos-material/` | Pedidos a proveedores |
| Pedido Items | `/api/pedido-items/` | Items de pedidos |
| Recepciones Material | `/api/recepciones-material/` | Recepciones |
| Recepción Items | `/api/recepcion-items/` | Items de recepciones |
| Inventario Material | `/api/inventario-material/` | Stock de materiales |
| Almacenes | `/api/almacenes/` | Gestión de almacenes |
| Entregas | `/api/entregas/` | Entregas a clientes |

### Operaciones CRUD

Cada endpoint soporta:
- `GET` - Listar todos
- `POST` - Crear nuevo
- `GET /{id}/` - Ver detalle
- `PUT /{id}/` - Actualizar completo
- `PATCH /{id}/` - Actualizar parcial
- `DELETE /{id}/` - Eliminar

### Filtros y Búsqueda

**Ejemplos de uso:**

```bash
# Buscar productos por código o nombre
GET /api/productos/?search=PROD001

# Filtrar lotes por estado
GET /api/lotes-produccion/?status=pending

# Filtrar por múltiples campos
GET /api/orden-items/?product=1&order=5

# Ordenar resultados
GET /api/productos/?ordering=-created_at

# Paginación
GET /api/productos/?page=2
```

## 🧪 Ejecutar Tests

```bash
# Ejecutar todos los tests
python manage.py test

# Ejecutar tests de una app específica
python manage.py test innoquim.apps.producto
python manage.py test innoquim.apps.usuario
python manage.py test innoquim.apps.lote_produccion

# Ejecutar tests con verbosidad
python manage.py test --verbosity=2

# Ejecutar tests y mantener la base de datos de test
python manage.py test --keepdb
```

## 📊 Modelos de Datos

### Usuario
- Email (único)
- Username (único)
- Nombre
- Rol (admin, manager, employee, client)

### Unidad
- Nombre
- Símbolo (kg, lb, etc.)
- Factor de conversión

### Producto
- Código de producto
- Nombre
- Descripción
- Unidad (FK)
- Peso

### Cliente
- Nombre
- Email
- Teléfono
- Dirección
- RUC/Identificación fiscal

### Orden Cliente
- Cliente (FK)
- Código de orden
- Fecha
- Estado
- Notas

### Orden Item
- Orden (FK)
- Producto (FK)
- Cantidad
- Unidad (FK)

### Materia Prima
- Nombre
- Código
- Descripción
- Unidad (FK)

### Lote Producción
- Producto (FK)
- Código de lote
- Fecha de producción
- Cantidad producida
- Unidad (FK)
- Estado
- Gerente de producción (FK Usuario)

### Material Producción
- Lote (FK)
- Materia prima (FK)
- Cantidad usada
- Unidad (FK)

## 🔐 Autenticación

La API utiliza autenticación de sesión por defecto. Para acceder a los endpoints protegidos:

1. Inicia sesión en el admin: http://localhost:8000/admin/
2. Una vez autenticado, puedes acceder a la API

O usa autenticación básica en las peticiones:
```bash
curl -u username:password http://localhost:8000/api/productos/
```

## 📝 Estructura del Proyecto

```
innoquim/
├── innoquim/
│   ├── apps/
│   │   ├── almacen/
│   │   ├── cliente/
│   │   ├── entrega/
│   │   ├── inventario_material/
│   │   ├── lote_produccion/
│   │   ├── materia_prima/
│   │   ├── material_produccion/
│   │   ├── orden_cliente/
│   │   ├── orden_item/
│   │   ├── pedido_item/
│   │   ├── pedido_material/
│   │   ├── producto/
│   │   ├── recepcion_item/
│   │   ├── recepcion_material/
│   │   ├── unidad/
│   │   └── usuario/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 🐛 Solución de Problemas

### Error: "No module named 'psycopg'"
```bash
pip install psycopg psycopg-binary
```

### Error: "relation does not exist"
```bash
python manage.py migrate
```

### Error: "FATAL: password authentication failed"
Verifica las credenciales en el archivo `.env`

### Error al crear migraciones
```bash
# Eliminar migraciones antiguas (SOLO EN DESARROLLO)
# Elimina los archivos en innoquim/apps/*/migrations/ excepto __init__.py
python manage.py makemigrations
python manage.py migrate
```

## 🔄 Actualizar el Proyecto

```bash
# Obtener últimos cambios
git pull origin main

# Actualizar dependencias
pip install -r requirements.txt

# Aplicar nuevas migraciones
python manage.py migrate

# Reiniciar servidor
python manage.py runserver
```
