from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    rol = models.CharField(unique=True, blank=False)

    def __str__(self):
        return f"{self.username}@{self.email}"