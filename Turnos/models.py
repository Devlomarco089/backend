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
    profesional = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.servicio.nombre} - {self.fecha} - {self.hora} - {'Disponible' if self.disponible else 'Ocupado'}"


class Turnos(models.Model):
    orden = models.ForeignKey("OrdenTurno", on_delete=models.CASCADE, related_name='turnos')
    horario = models.ForeignKey(HorarioDisponible, on_delete=models.CASCADE)
    profesional = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="turnos_asignados")
    servicio = models.ForeignKey(Servicios, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.orden.usuario.username} - {self.horario.servicio.nombre} - {self.horario.fecha} - {self.horario.hora}"


class OrdenTurno(models.Model):
    METODOS_PAGO = (
        ("web", "Web"),
        ("efectivo", "Efectivo"),
    )

    TIPOS_TARJETA = (
        ("debito", "Débito"),
        ("credito", "Crédito"),
    )

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    pagado = models.BooleanField(default=False)
    descuento_aplicado = models.BooleanField(default=False)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, null=True, blank=True)
    tipo_tarjeta = models.CharField(max_length=10, choices=TIPOS_TARJETA, null=True, blank=True)
    fecha_pago = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Orden de {self.usuario.username} - Total: {self.total}"