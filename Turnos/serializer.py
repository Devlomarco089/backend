from rest_framework import serializers
from .models import Turnos


class TurnoSerializer(serializers.ModelSerializer):
    servicio_nombre = serializers.CharField(source="horario.servicio.nombre", read_only=True)  # Devuelve el nombre del servicio
    fecha = serializers.DateField(source="horario.fecha", read_only=True)  # Devuelve la fecha del horario
    hora = serializers.TimeField(source="horario.hora", read_only=True)  # Devuelve la hora del horario 

    class Meta:
        model = Turnos
        fields = '__all__'
        