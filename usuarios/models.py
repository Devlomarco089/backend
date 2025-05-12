from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Correo Electrónico')
    username = models.CharField(max_length=150, blank=True, null=True)  # Hacer opcional

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    def __str__(self):
        return self.email
