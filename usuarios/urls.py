from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import UsuarioRegisterView, VerifyEmailView, ProfessionalSelfUpdateViewSet, TestAuthView


#admin
router = DefaultRouter()


#profesionales
router.register('mi-perfil/profesional', ProfessionalSelfUpdateViewSet, basename='profesional-self')

urlpatterns = [
    path('register/', UsuarioRegisterView.as_view(), name='usuario_register'),
    path('verifi-email/<uidb64>/<token>/',VerifyEmailView.as_view(), name='verify_email'),
    path('admin/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # Refresh
    path('test-auth/', TestAuthView.as_view(), name='test-auth'),
]

