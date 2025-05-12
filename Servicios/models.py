from django.db import models



class Servicios(models.Model):
    CATEGORIA_CHOICES = [
        ('masajes', 'Masajes'),
        ('belleza', 'Belleza'),
        ('faciales', 'Faciales'),
        ('corporal', 'Corporal'),
        ('grupal', 'Grupal'),
        ]
    imagen = models.ImageField(upload_to='servicios/' , blank=True, null=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    duracion = models.IntegerField()  
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='masajes')

    def __str__(self):
        return self.nombre

