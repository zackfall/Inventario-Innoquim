from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('innoquim.apps.cliente.urls')),      # API de Clientes
    path('api/', include('innoquim.apps.proveedor.urls')),    # API de Proveedor
]