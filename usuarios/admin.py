from django.contrib import admin
from .models import CustomUser, Professional

# Register your models here.

#admin.site.register(CustomUser)
class ProfesionalInline(admin.StackedInline):
    model = Professional
    can_delete = False
    verbose_name_plural = "Información profesional"
    fk_name = 'user'
    extra = 0

@admin.register(CustomUser)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'tipo_usuario')
    search_fields = ('email',)
    list_filter = ('tipo_usuario',)

    fieldsets = (
        ('Datos básicos', {
            'fields': ('email', 'first_name', 'last_name', 'tipo_usuario')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups'),
            'classes': ('collapse',),
        }),
        ('Fechas importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',),
        }),
    )

    # Mostrar inline de profesional solo si el usuario es profesional
    def get_inline_instances(self, request, obj=None):
        inlines = []
        if obj and obj.tipo_usuario == 'profesional':
            inlines.append(ProfesionalInline(self.model, self.admin_site))
        return inlines