from django.urls import path
from .views import TurnoListCreateView, HorariosDisponiblesView, ReservarTurnosView, PagarOrdenView, TurnosPDFAPIView, TurnosTomorrowAPIView, TurnosPorDiaPorServicioAPIView, TotalesPagadosPorServicioAPIView, TotalesPagadosPorProfesionalView

urlpatterns = [
    path('turnos/', TurnoListCreateView.as_view(), name='turno-list-create'),
    path('horarios-disponibles/', HorariosDisponiblesView.as_view(), name='horarios-disponibles'),
    path('reservar-turno/', ReservarTurnosView.as_view(), name='reservar-turno'),
    path('pagar-orden/<int:orden_id>/', PagarOrdenView.as_view(), name='pagar-orden'),
    path('turnos-tomorrow/', TurnosTomorrowAPIView.as_view(), name='turnos'),
    path('turnos-tomorrow/pdf/', TurnosPDFAPIView.as_view(), name='turnos-pdf'),
    path('turnos-por-dia/', TurnosPorDiaPorServicioAPIView.as_view(), name='lista-turnos'),
    path('totales-pagados-servicio/', TotalesPagadosPorServicioAPIView.as_view(), name='totales-pagados-servicio'),
    path('totales-pagados-profesional/', TotalesPagadosPorProfesionalView.as_view(), name='totales-pagados-profesional'),
]