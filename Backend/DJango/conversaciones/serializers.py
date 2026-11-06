from rest_framework import serializers
from .models import Conversacion, Mensaje

class MensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensaje
        fields = ['id','conversacion', 'rol', 'contenido', 'fecha_envio']

class ConversacionSerializer(serializers.ModelSerializer):
    mensajes = MensajeSerializer(many=True, read_only=True)

    class Meta:
        model = Conversacion
        fields = ['id', 'fecha_creacion', 'mensajes']