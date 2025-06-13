from django.shortcuts import render
from rest_framework import status
from .models import Turnos, HorarioDisponible, OrdenTurno
from .serializer import TurnoSerializer, OrdenTurnoSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta, date
from django.core.mail import send_mail
from decimal import Decimal
from collections import defaultdict
from .utils import enviar_comprobante_pago
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from calendar import monthrange
from django.db.models import F, Sum

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
                profesional = h.profesional
                if not profesional:
                    return Response({"error": f"El servicio '{h.servicio}' no tiene un profesional asignado."}, status=400)
                
                Turnos.objects.create(
                    orden=orden,
                    horario=h,
                    profesional=profesional,
                    servicio=h.servicio
                )
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
        

class TurnosTomorrowAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario = request.user
        tomorrow = datetime.now().date() + timedelta(days=1)

        turnos = Turnos.objects.filter(
            horario__fecha=tomorrow,
            profesional=usuario
        ).select_related("orden__usuario", "horario", "servicio").order_by("horario__hora")

        serializer = TurnoSerializer(turnos, many=True)
        return Response(serializer.data)


class TurnosPDFAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario = request.user
        tomorrow = datetime.now().date() + timedelta(days=1)

        turnos = Turnos.objects.filter(
            horario__fecha=tomorrow,
            profesional=usuario
        ).select_related("orden__usuario", "horario", "servicio").order_by("horario__hora")

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        styles = getSampleStyleSheet()
        elements.append(Paragraph(f"Turnos para el día {tomorrow.strftime('%d/%m/%Y')}", styles["Title"]))
        elements.append(Spacer(1, 12))

        if not turnos:
            elements.append(Paragraph("No hay turnos asignados.", styles["Normal"]))
        else:
            data = [["Hora", "Paciente", "Email", "Servicio"]]
            for turno in turnos:
                hora = turno.horario.hora.strftime("%H:%M")
                nombre = f"{turno.orden.usuario.first_name} {turno.orden.usuario.last_name}"
                email = turno.orden.usuario.email
                servicio = turno.servicio.nombre if hasattr(turno.servicio, "nombre") else str(turno.servicio)
                data.append([hora, nombre, email, servicio])

            table = Table(data, colWidths=[60, 150, 180, 150])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            elements.append(table)

        doc.build(elements)

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="turnos_{tomorrow.strftime("%d_%m_%Y")}.pdf"'
        return response
    


class TurnosPorDiaPorServicioAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fecha_str = request.query_params.get("fecha")
        if not fecha_str:
            return Response({"error": "Debe proveer la fecha en formato YYYY-MM-DD"}, status=400)
        
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Formato de fecha inválido, debe ser YYYY-MM-DD"}, status=400)

        # Filtro turnos por fecha
        turnos = Turnos.objects.filter(horario__fecha=fecha).select_related(
            "orden__usuario", "profesional", "servicio", "horario"
        ).order_by("servicio__nombre", "horario__hora")

        # Se agrupa por servicio
        turnos_por_servicio = defaultdict(list)
        for turno in turnos:
            servicio_nombre = turno.servicio.nombre if hasattr(turno.servicio, "nombre") else str(turno.servicio)
            turno_info = {
                "hora": turno.horario.hora.strftime("%H:%M"),
                "paciente": f"{turno.orden.usuario.first_name} {turno.orden.usuario.last_name}",
                "email_paciente": turno.orden.usuario.email,
                "profesional": turno.profesional.get_full_name() or turno.profesional.username,
            }
            turnos_por_servicio[servicio_nombre].append(turno_info)

        return Response({
            fecha_str: turnos_por_servicio
        })
    


class TotalesPagadosPorServicioAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')

        if not fecha_inicio or not fecha_fin:
            # Si no se pasan fechas, se usa el mes actual completo
            hoy = date.today()
            primer_dia = date(hoy.year, hoy.month, 1)
            ultimo_dia = date(hoy.year, hoy.month, monthrange(hoy.year, hoy.month)[1])
            fecha_inicio_dt = primer_dia
            fecha_fin_dt = ultimo_dia
        else:
            try:
                fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
                fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
            except (TypeError, ValueError):
                return Response(
                    {"error": "Parámetros fecha_inicio y fecha_fin con formato YYYY-MM-DD son obligatorios."},
                    status=400
                )

        turnos = Turnos.objects.filter(
            horario__fecha__gte=fecha_inicio_dt,
            horario__fecha__lte=fecha_fin_dt,
            orden__pagado=True
        ).values(
            servicio_nombre=F('servicio__nombre')
        ).annotate(
            total_pagado=Sum('orden__total')
        ).order_by('servicio_nombre')

        return Response({
            "fecha_inicio": fecha_inicio_dt,
            "fecha_fin": fecha_fin_dt,
            "totales": turnos
        })
    

class TotalesPagadosPorProfesionalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fecha_inicio_str = request.query_params.get('fecha_inicio')
        fecha_fin_str = request.query_params.get('fecha_fin')

        hoy = datetime.now().date()
        if not fecha_inicio_str or not fecha_fin_str:
            # Primer día del mes actual
            fecha_inicio = hoy.replace(day=1)
            # Último día del mes actual
            fecha_fin = (fecha_inicio + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        else:
            fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
            fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()

        # Consulta: sumar totales pagados por profesional en el rango de fechas
        # join entre Turnos y OrdenTurno, filtro por orden pagada y fecha_pago dentro del rango 
        queryset = (
            Turnos.objects.filter(
                orden__pagado=True,
                orden__fecha_pago__date__gte=fecha_inicio,
                orden__fecha_pago__date__lte=fecha_fin,
            )
            .values(profesional_id=F('profesional__id'), profesional_nombre=F('profesional__username'))
            .annotate(total_pagado=Sum('orden__total'))
            .order_by('profesional_nombre')
        )

        return Response({
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "totales_por_profesional": list(queryset)
        })