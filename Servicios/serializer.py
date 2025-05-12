from rest_framework import serializers
from .models import Servicios

class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicios
        fields = '__all__'