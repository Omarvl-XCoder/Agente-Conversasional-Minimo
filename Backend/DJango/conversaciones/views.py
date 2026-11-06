from rest_framework import viewsets
from .models import Conversacion, Mensaje
from .serializers import ConversacionSerializer, MensajeSerializer

class ConversacionViewSet(viewsets.ModelViewSet):
    queryset = Conversacion.objects.all().order_by('-fecha_creacion')
    serializer_class = ConversacionSerializer

class MensajeViewSet(viewsets.ModelViewSet):
    queryset = Mensaje.objects.all().order_by('fecha_envio')
    serializer_class = MensajeSerializer