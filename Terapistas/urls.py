from django.urls import path
from .views import TerapistaListView

urlpatterns = [
    path('terapistas/', TerapistaListView.as_view(), name='terapista-list'),
    ]
