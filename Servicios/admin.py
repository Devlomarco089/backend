from django.contrib import admin
from .models import Servicios

@admin.register(Servicios)
class ServiciosAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'duracion', 'fecha_creacion', 'fecha_actualizacion', 'profesionales_count', 'imagen_preview')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('categoria', 'fecha_creacion', 'fecha_actualizacion')
    filter_horizontal = ('profesional',)

    readonly_fields = ('imagen_preview',)

    def profesionales_count(self, obj):
        return obj.profesional.count()
    profesionales_count.short_description = 'Cantidad de profesionales'

    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="width: 75px; height: auto;" />', obj.imagen.url)
        return "-"
    imagen_preview.short_description = 'Imagen'
