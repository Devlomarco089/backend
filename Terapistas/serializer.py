from rest_framework import serializers
from .models import Terapista

class TerapistaSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Terapista
        fields = '__all__'