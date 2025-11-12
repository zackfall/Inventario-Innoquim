from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('innoquim.apps.cliente.urls')),      # API de Clientes
    path('api/', include('innoquim.apps.proveedor.urls')),    # API de Proveedor
    path('api/', include('innoquim.apps.materia_prima.urls')), # API de Materia Prima
    path('api/', include('innoquim.apps.inventario_material.urls')), # API de Inventario_Material
    path('api/', include('innoquim.apps.pedido_material.urls')), # API de Pedido_material
]
