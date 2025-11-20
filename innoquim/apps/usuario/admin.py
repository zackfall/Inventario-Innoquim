from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

Usuario = get_user_model()


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = ["email", "username", "name", "rol", "is_active", "is_staff"]
    list_filter = ["rol", "is_active", "is_staff"]
    search_fields = ["email", "username", "name"]
    ordering = ["email"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Información Personal", {"fields": ("username", "name", "rol")}),
        (
            "Permisos",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Fechas Importantes", {"fields": ("last_login", "created_at", "updated_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "name",
                    "rol",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    readonly_fields = ["created_at", "updated_at", "last_login"]
