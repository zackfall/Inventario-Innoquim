# Plataforma CEISH

## Pasos para desarrolladores
Primero tenemos que clonar el repositorio.
```powershell
$ git clone https://github.com/zackfall/Inventario-Innoquim
```
Para los desarrolladores, recomendable instalar pyenv para manejar las versiones de python,
ya que este proyecto usa python 3.12 en vez de la ultima versiòn. Para instalar pyenv sigan los pasos.

## Instalación de Pyenv
1. Abrir Powershell y escribir el siguiente comando.
```powershell
$ Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
```
> [!NOTE]
> Recomendable usar el powershell en modo administrador para que no le genere ningún error.
2. Abre nuevamente PowerShell y escribe este comando para verificar si la instalación fue correcta.
```powershell
$ pyenv --version
```
3. Ahora instala la versiòn de python
```powershell
$ pyenv install 3.12
```
4. Ahora activa el el entorno de desarrollo.
```powershell
$ pyenv global 3.12
```
5. Ahora verificamos si todo funciona correctamente, tendrìa que salir algo similar a esto:
```powershell
$ pyenv version
3.12 (set by \path\to\.pyenv\pyenv-win\.python-version)
```
6. Por ultimo tenemos que instalar todos los requerimientos dentro de `requirements.txt`.
```powershell
$ python -m pip install -r requirements.txt
```

## Configurar el archivo .env y la base de datos.
En la carpeta del proyecto se encuentra un archivo llamado `.env.example`, lo que hay que hacer es ir configurando las variables de entorno para que el proyecto funcione correctamente.

Para la variable `SECRET_KEY`, hay que abrir el powershell y hacer lo siguiente.
1. Abrir la terminal de python
```powershell
$ python
```
2. Escribir el siguiente código
```py
import secrets

secret_key = secrets.token_urlsafe(64) # Esto genera una clave secreta de 64 bits
print(secret_key)
```
3. pegar el resultado del print en la llave secreta.
```
SECRET_TOKEN="Aquí va la llave generada."
```

El DEBUG dejarlo como está mientras siga en desarrollo, una vez la aplicación entre en estado de producción, cambiarlo a False.

Ahora, para la base de datos, deben de ir cambiando los valores según la base de datos que creén en su computador, luego solo cambiarle el nombre para que quede solo `.env`.

Por último deben ejecutar este comando en la carpeta raíz del proyecto para que se ejecuten las migraciones de la base de datos.
```powershell
$ python manage.py migrate
```

Despuès de todos estos pasos ya estaría todo listo para comenzar a desarrollar.
