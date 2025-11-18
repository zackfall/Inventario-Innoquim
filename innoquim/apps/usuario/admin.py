from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario

# Register your models here.
class UsuarioAdmim(UserAdmin):
    model = Usuario
    list_display = [
        "email",
        "username",
        "is_staff",
        "is_active",
        "rol"
    ]

admin.site.register(Usuario, UsuarioAdmim)