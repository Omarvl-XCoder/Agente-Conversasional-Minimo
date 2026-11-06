from django.contrib import admin
from .models import Conversacion, Mensaje

admin.site.site_header = "Agente Conversacional - Administración"
admin.site.site_title = "Agente Conversacional"
admin.site.index_title = "Panel de gestión"


class MensajeInline(admin.TabularInline):
    model = Mensaje
    extra = 0
    fields = ("rol", "contenido", "fecha_envio")
    readonly_fields = ("fecha_envio",)


@admin.register(Conversacion)
class ConversacionAdmin(admin.ModelAdmin):
    list_display = ("id", "fecha_creacion", "total_mensajes")
    list_filter = ("fecha_creacion",)
    date_hierarchy = "fecha_creacion"
    ordering = ("-fecha_creacion",)
    inlines = [MensajeInline]

    @admin.display(description="Mensajes")
    def total_mensajes(self, obj):
        return obj.mensajes.count()


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ("id", "conversacion", "rol", "resumen", "fecha_envio")
    list_filter = ("rol", "fecha_envio")
    search_fields = ("contenido",)
    list_select_related = ("conversacion",)
    ordering = ("-fecha_envio",)
    readonly_fields = ("fecha_envio",)

    @admin.display(description="Contenido")
    def resumen(self, obj):
        return obj.contenido[:60] + ("..." if len(obj.contenido) > 60 else "")