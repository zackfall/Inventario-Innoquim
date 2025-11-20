from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UsuarioManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("El usuario debe tener un email")
        if not username:
            raise ValueError("El usuario debe tener un username")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("rol", "admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser debe tener is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser debe tener is_superuser=True")

        return self.create_user(email, username, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    ROLES = (
        ("admin", "Administrador"),
        ("manager", "Gerente"),
        ("employee", "Empleado"),
        ("client", "Cliente"),
    )

    email = models.EmailField(unique=True, max_length=255)
    username = models.CharField(unique=True, max_length=150)
    name = models.CharField(max_length=255)
    rol = models.CharField(max_length=20, choices=ROLES, default="employee")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "name"]

    class Meta:
        db_table = "usuario"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return f"{self.name} ({self.email})"
