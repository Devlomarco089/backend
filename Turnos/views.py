from django.shortcuts import render
from rest_framework import status
from .models import Turnos, HorarioDisponible
from .serializer import TurnoSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from datetime import datetime

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