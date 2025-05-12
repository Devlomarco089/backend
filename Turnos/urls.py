from django.urls import path
from .views import TurnoListCreateView, HorariosDisponiblesView

urlpatterns = [
    path('turnos/', TurnoListCreateView.as_view(), name='turno-list-create'),
    path('horarios-disponibles/', HorariosDisponiblesView.as_view(), name='horarios-disponibles'),
]