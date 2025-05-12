from django.shortcuts import render
from .serializer import ServicioSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Servicios
from rest_framework import status
from rest_framework.permissions import AllowAny



class ServicioListCreateView(APIView):
    permission_classes = [AllowAny]  

    def get(self, request):
        category = request.query_params.get('category', None)

        if category:
            servicios = Servicios.objects.filter(categoria=category)
        else:
            servicios = Servicios.objects.all()

        serializer = ServicioSerializer(servicios, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ServicioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)