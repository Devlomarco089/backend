from django.urls import path
from .views import ServicioListCreateView
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('servicios/', ServicioListCreateView.as_view(), name='servicio-list-create'),
    path('servicios/<int:pk>/', ServicioListCreateView.as_view(), name='servicio-detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)