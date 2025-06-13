from django.contrib import admin
from .models import HorarioDisponible, Turnos, OrdenTurno


# Inline para mostrar turnos dentro de la OrdenTurno
class TurnosInline(admin.TabularInline):
    model = Turnos
    extra = 0  # No mostrar formularios vacíos adicionales
    readonly_fields = ('profesional', 'horario', 'servicio')


@admin.register(HorarioDisponible)
class HorarioDisponibleAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'hora', 'profesional', 'servicio', 'disponible')
    list_filter = ('fecha', 'disponible', 'profesional', 'servicio')
    search_fields = ('profesional__email', 'servicio__nombre')
    ordering = ('fecha', 'hora')


@admin.register(Turnos)
class TurnosAdmin(admin.ModelAdmin):
    list_display = ('orden', 'horario', 'profesional', 'servicio')
    list_filter = ('servicio', 'profesional')
    search_fields = ('orden__usuario__email', 'profesional__email', 'servicio__nombre')


@admin.register(OrdenTurno)
class OrdenTurnoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha_creacion', 'pagado', 'total', 'metodo_pago', 'tipo_tarjeta')
    list_filter = ('pagado', 'metodo_pago', 'tipo_tarjeta', 'fecha_creacion')
    search_fields = ('usuario__email',)
    readonly_fields = ('fecha_creacion', 'fecha_pago')
    inlines = [TurnosInline]