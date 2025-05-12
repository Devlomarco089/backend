from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import get_object_or_404
from .serializer import UserSerializer
from .utils import generate_email_verification_link
from .models import CustomUser


class UsuarioRegisterView(APIView):
    permission_classes = [AllowAny] 

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False 
            user.save()

            
            verification_link = generate_email_verification_link(user, request)

            try:
                send_mail(
                    'Verifica tu correo electrónico',
                    f'Por favor, verifica tu correo haciendo clic en el siguiente enlace: {verification_link}',
                    'SpaSentirseBien@SpaSentirseBien.com',  
                    [user.email],
                    fail_silently=False,
                )
            except Exception as e:
                return Response({
                    'message': 'Error al enviar el correo de verificación. Inténtalo de nuevo más tarde.',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                'message': 'Usuario registrado con éxito. Por favor, verifica tu correo electrónico.',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                },
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'message': 'Error en el registro de usuario.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(CustomUser, pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True 
            user.save()
            return Response({'message': 'Correo verificado con éxito. Ahora puedes iniciar sesión.'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'El enlace de verificación no es válido o ha expirado.'}, status=status.HTTP_400_BAD_REQUEST)