from django.urls import path
from .views import UsuarioRegisterView, VerifyEmailView

urlpatterns = [
    path('register/', UsuarioRegisterView.as_view(), name='usuario_register'),
    path('verifi-email/<uidb64>/<token>/',VerifyEmailView.as_view(), name='verify_email')
]
