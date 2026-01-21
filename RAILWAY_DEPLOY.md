# Instrucciones de Despliegue en Railway

## Configuración del Proyecto

Este proyecto está listo para desplegarse en Railway. Se han configurado los siguientes archivos:

- ✅ `railway.json` - Configuración de Railway
- ✅ `nixpacks.toml` - Configuración de build
- ✅ `Dockerfile` - Configuración de Docker para producción
- ✅ `innoquim/settings.py` - Ajustado para Railway con WhiteNoise y dj-database-url
- ✅ `requirements.txt` - Dependencias actualizadas

## Pasos para Desplegar

### 1. Inicializar Git (si no está inicializado)

```powershell
git init
git add .
git commit -m "Configuración inicial para Railway"
```

### 2. Crear Proyecto en Railway

1. Ve a [railway.app](https://railway.app) e inicia sesión
2. Click en "New Project"
3. Selecciona "Deploy from GitHub repo"
4. O usa "Empty Project" si prefieres desplegar desde CLI

### 3. Agregar PostgreSQL

1. En tu proyecto de Railway, click en "+ New"
2. Selecciona "Database" → "Add PostgreSQL"
3. Railway automáticamente creará la variable `DATABASE_URL`

### 4. Agregar Redis (Opcional pero recomendado)

1. Click en "+ New" nuevamente
2. Selecciona "Database" → "Add Redis"
3. Railway creará automáticamente las variables de Redis

### 5. Configurar Variables de Entorno

En la sección "Variables" del servicio Django, agrega:

```
SECRET_KEY=<genera-una-clave-secreta-segura>
DEBUG=False
ALLOWED_HOSTS=*
REDIS_HOST=<host-de-redis-si-lo-agregaste>
REDIS_PORT=6379
REDIS_DB=0
```

### 6. Desplegar desde CLI (Opción A)

```powershell
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Vincular proyecto
railway link

# Desplegar
railway up
```

### 7. Desplegar desde GitHub (Opción B - Recomendado)

1. Sube tu código a GitHub:
   ```powershell
   git remote add origin https://github.com/tu-usuario/tu-repo.git
   git push -u origin main
   ```

2. En Railway:
   - Click en "New Project"
   - "Deploy from GitHub repo"
   - Selecciona tu repositorio
   - Railway detectará automáticamente el Dockerfile

### 8. Ejecutar Migraciones

Una vez desplegado, abre la terminal de Railway:

```bash
python manage.py createsuperuser
```

### 9. Verificar Despliegue

Railway te proporcionará una URL pública. Accede a:
- API: `https://tu-app.railway.app/`
- Admin: `https://tu-app.railway.app/admin/`

## Notas Importantes

- ✅ El Dockerfile ejecuta `migrate` automáticamente en cada deploy
- ✅ Los archivos estáticos se sirven con WhiteNoise
- ✅ La base de datos PostgreSQL se configura automáticamente
- ⚠️ Asegúrate de generar un `SECRET_KEY` seguro para producción
- ⚠️ Configura `DEBUG=False` en producción

## Comandos Útiles de Railway

```powershell
# Ver logs
railway logs

# Ejecutar comandos
railway run python manage.py createsuperuser

# Ver variables de entorno
railway variables

# Abrir dashboard
railway open
```
