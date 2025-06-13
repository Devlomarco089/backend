from django.urls import path
from .views import TurnoListCreateView, HorariosDisponiblesView, ReservarTurnosView, PagarOrdenView

urlpatterns = [
    path('turnos/', TurnoListCreateView.as_view(), name='turno-list-create'),
    path('horarios-disponibles/', HorariosDisponiblesView.as_view(), name='horarios-disponibles'),
    path('reservar-turno/', ReservarTurnosView.as_view(), name='reservar-turno'),
    path('pagar-orden/<int:orden_id>/', PagarOrdenView.as_view(), name='pagar-orden'),
]