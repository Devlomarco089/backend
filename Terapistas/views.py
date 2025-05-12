from django.shortcuts import render
from .models import Terapista
from django.views.generic import ListView


class TerapistaListView(ListView):
    model = Terapista
    template_name = 'terapistas/terapista_list.html'
    context_object_name = 'terapistas'

    def get_queryset(self):
        return Terapista.objects.all()
