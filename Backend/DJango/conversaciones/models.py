from django.db import models

class Conversacion(models.Model):
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversación {self.id} - {self.fecha_creacion.strftime('%d/%m/%Y %H:%M')}"

class Mensaje(models.Model):
    ROLES = (
        ('usuario', 'Usuario'),
        ('agente', 'Agente IA'),
    )
    conversacion = models.ForeignKey(Conversacion, on_delete=models.CASCADE, related_name='mensajes')
    rol = models.CharField(max_length=10, choices=ROLES)
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.get_rol_display()}] {self.contenido[:30]}..."