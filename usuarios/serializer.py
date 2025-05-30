from .models import CustomUser, Professional
from rest_framework import serializers


class ProfessionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professional
        fields = ['especiality', 'experience', 'certificaciones', 'disponibilidad_horaria', 'profile_picture']

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(required=True)  # Obligatorio
    last_name = serializers.CharField(required=True)  # Obligatorio
    datos_profesional = ProfessionalSerializer(required=False)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'password', 'first_name', 'last_name', 'tipo_usuario', 'datos_profesional')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        professional_data = validated_data.pop('datos_profesional', None)
        user = CustomUser(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data.get('username', ''),  # Opcional
            tipo_usuario=validated_data.get('tipo_usuario', 'cliente')
        )

        user.set_password(validated_data['password'])
        user.save()
        
        if user.tipo_usuario == 'profesional' and professional_data:
            especiality = professional_data.pop('especiality', [])
            profesional = Professional.objects.create(user=user, **professional_data)
            profesional.especiality.set(especiality)
            profesional.save()

        return user