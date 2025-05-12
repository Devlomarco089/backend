from .models import CustomUser
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    username = serializers.CharField(required=False, allow_blank=True)  # Hacer opcional

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'password')

    def create(self, validated_data):
        user = CustomUser(
            email=validated_data['email'],
            username=validated_data.get('username', '')  # Asignar un valor predeterminado si no se proporciona
        )
        user.set_password(validated_data['password'])
        user.save()
        return user