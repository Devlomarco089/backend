from django.db import models
from django.contrib.auth.models import User
from Servicios.models import Servicios
from django.conf import settings
# Create your models here.

class HorarioDisponible(models.Model):
    servicio = models.ForeignKey(Servicios, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    disponible = models.BooleanField(default=True)  # Indica si el horario está disponible

    def __str__(self):
        return f"{self.servicio.nombre} - {self.fecha} - {self.hora} - {'Disponible' if self.disponible else 'Ocupado'}"


class Turnos(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    horario = models.ForeignKey(HorarioDisponible, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.usuario.username} - {self.horario.servicio.nombre} - {self.horario.fecha} - {self.horario.hora}"

