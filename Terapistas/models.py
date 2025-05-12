from django.db import models

# Create your models here.


class Terapista(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100)
    experiencia = models.TextField()

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
