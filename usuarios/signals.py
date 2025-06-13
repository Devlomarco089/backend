from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Professional
from Servicios.models import Servicios

@receiver(m2m_changed, sender=Professional.especiality.through)
def asignar_profesional_a_servicios(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        for servicio_id in pk_set:
            servicio = Servicios.objects.get(pk=servicio_id)
            servicio.profesional.add(instance)  # Agrega sin reemplazar