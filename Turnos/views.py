from django.shortcuts import render
from rest_framework import status
from .models import Turnos, HorarioDisponible, OrdenTurno
from .serializer import TurnoSerializer, OrdenTurnoSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta
from django.core.mail import send_mail
from decimal import Decimal
from collections import defaultdict
from .utils import enviar_comprobante_pago

class TurnoListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        turnos = Turnos.objects.filter(usuario=user)
        serializer = TurnoSerializer(turnos, many=True)
        return Response(serializer.data)

    def post(self, request):
        horario_id = request.data.get("horario")
        if not horario_id:
            return Response(
                {"error": "Se requiere un horario."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            horario = HorarioDisponible.objects.get(id=horario_id, disponible=True)
        except HorarioDisponible.DoesNotExist:
            return Response(
                {"error": "El horario no está disponible."},
                status=status.HTTP_400_BAD_REQUEST
            )

        turno = Turnos.objects.create(usuario=request.user, horario=horario)
        horario.disponible = False
        horario.save()

        serializer = TurnoSerializer(turno)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class HorariosDisponiblesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        servicio_id = request.query_params.get("servicio")
        fecha = request.query_params.get("fecha")

        if not servicio_id or not fecha:
            return Response(
                {"error": "Se requiere el servicio y la fecha."},
                status=status.HTTP_400_BAD_REQUEST
            )

        horarios = HorarioDisponible.objects.filter(
            servicio_id=servicio_id,
            fecha=fecha,
            disponible=True
        ).order_by('hora')

        horarios_disponibles = [
            {"id": horario.id, "hora": horario.hora.strftime("%H:%M")}
            for horario in horarios
        ]

        return Response(horarios_disponibles, status=status.HTTP_200_OK)
    

#Carrito solo para turnos y servicios
class ReservarTurnosView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        horarios_ids = request.data.get("horarios", [])

        if not horarios_ids:
            return Response({"error": "Debe seleccionar al menos un horario."}, status=400)

        horarios = HorarioDisponible.objects.filter(id__in=horarios_ids, disponible=True).select_related("servicio")

        if horarios.count() != len(horarios_ids):
            return Response({"error": "Uno o más horarios ya no están disponibles."}, status=400)

        grupos_por_fecha = defaultdict(list)
        for h in horarios:
            if h.fecha < datetime.now().date() + timedelta(days=2):
                return Response({"error": f"El turno del {h.fecha} debe reservarse al menos 48 hs antes."}, status=400)
            grupos_por_fecha[h.fecha].append(h)

        ordenes_serializadas = []

        for fecha, horarios_en_fecha in grupos_por_fecha.items():
            total = sum([h.servicio.precio for h in horarios_en_fecha])

            orden = OrdenTurno.objects.create(
                usuario=request.user,
                total=total,
                pagado=False,
                descuento_aplicado=False  # aún no se paga
            )

            for h in horarios_en_fecha:
                Turnos.objects.create(orden=orden, horario=h)
                h.disponible = False
                h.save()

            ordenes_serializadas.append(OrdenTurnoSerializer(orden).data)

        return Response(ordenes_serializadas, status=status.HTTP_201_CREATED)
    

class PagarOrdenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, orden_id):
        metodo_pago = request.data.get("metodo_pago")  # "web" o "efectivo"
        tipo_tarjeta = request.data.get("tipo_tarjeta")     # "debito" o "credito" (solo si es web)

        try:
            orden = OrdenTurno.objects.get(id=orden_id, usuario=request.user)
        except OrdenTurno.DoesNotExist:
            return Response({"error": "Orden no encontrada."}, status=404)

        if orden.pagado:
            return Response({"error": "La orden ya fue pagada."}, status=400)

        fechas = orden.turnos.all().values_list('horario__fecha', flat=True).distinct()
        if len(fechas) != 1:
            return Response({"error": "Error interno: la orden contiene fechas diferentes."}, status=400)

        fecha_turno = fechas[0]
        hoy = datetime.now().date()
        dentro_de_48hs = fecha_turno <= hoy + timedelta(days=2)

        total = orden.total
        descuento_aplicado = False

        if metodo_pago == "web":
            if not tipo_tarjeta or tipo_tarjeta.lower() not in ["debito", "credito"]:
                return Response({"error": "Debe especificar si la tarjeta es de débito o crédito."}, status=400)

            if tipo_tarjeta == "debito" and not dentro_de_48hs:
                total *= Decimal("0.85")
                descuento_aplicado = True

            orden.pagado = True
            orden.metodo_pago = "web"
            orden.tipo_tarjeta = tipo_tarjeta
            orden.fecha_pago = datetime.now()
            orden.total = total
            orden.descuento_aplicado = descuento_aplicado
            orden.save()
            enviar_comprobante_pago(orden)

            return Response({
                "mensaje": "Pago web realizado con éxito.",
                "orden": {
                    "id": orden.id,
                    "fecha_turno": fecha_turno,
                    "total": f"${total:.2f}",
                    "descuento_aplicado": descuento_aplicado,
                    "pagado": True,
                    "metodo": metodo_pago,
                    "tarjeta": tipo_tarjeta
                }
            }, status=200)

        elif metodo_pago == "efectivo":
            orden.pagado = False
            orden.metodo_pago = "efectivo"
            orden.tipo_tarjeta = None
            orden.fecha_pago = None
            orden.descuento_aplicado = False
            orden.save()

            return Response({
                "mensaje": "Pago en efectivo registrado. Se abonará el día del turno.",
                "orden": {
                    "id": orden.id,
                    "fecha_turno": fecha_turno,
                    "total": f"${total:.2f}",
                    "pagado": False,
                    "metodo": "efectivo"
                }
            }, status=200)

        else:
            return Response({"error": "Método de pago inválido. Use 'web' o 'efectivo'."}, status=400)
        
        