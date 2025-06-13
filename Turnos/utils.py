from datetime import datetime, timedelta, time
from .models import HorarioDisponible
from Servicios.models import Servicios
from django.core.mail import send_mail

def inicializar_horarios(servicio_id, fecha_inicio, fecha_fin):
    servicio = Servicios.objects.get(id=servicio_id)
    horario_inicio = time(8, 0)  # 8:00 AM
    horario_fin = time(18, 0)  # 6:00 PM

    fecha_actual = fecha_inicio
    while fecha_actual <= fecha_fin:
        hora_actual = horario_inicio
        while hora_actual < horario_fin:
            HorarioDisponible.objects.get_or_create(
                servicio=servicio,
                fecha=fecha_actual,
                hora=hora_actual,
                defaults={'disponible': True}
            )
            hora_actual = (datetime.combine(fecha_actual, hora_actual) + timedelta(hours=1)).time()
        fecha_actual += timedelta(days=1)


def enviar_comprobante_pago(orden):
    subject = f"Comprobante de pago - Orden #{orden.id}"
    message = (
        f"Hola {orden.usuario.username},\n\n"
        f"Gracias por tu pago. Aquí están los detalles de tu orden:\n"
        f"Fecha de turno: {orden.turnos.first().horario.fecha}\n"
        f"Total pagado: ${orden.total}\n"
        f"Método de pago: {orden.metodo_pago}\n"
        f"Tipo de tarjeta: {orden.tipo_tarjeta if orden.tipo_tarjeta else 'N/A'}\n\n"
        "Saludos,\nTu equipo de Turnos"
    )
    recipient = [orden.usuario.email]
    send_mail(subject, message, None, recipient)