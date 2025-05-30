from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)
    
    def create_profesional(self, email, password=None, **extra_fields):
        extra_fields.setdefault('tipo_usuario', 'profesional')
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Correo Electrónico')
    first_name = models.CharField(max_length=150, verbose_name='Nombre')
    last_name = models.CharField(max_length=150, verbose_name='Apellido')
    username = models.CharField(max_length=150, blank=True, null=True)  # Opcional

    USERNAME_FIELD = 'email'  # Identificador para iniciar sesión
    REQUIRED_FIELDS = ['first_name', 'last_name']  # Campos obligatorios al crear un usuario

    objects = CustomUserManager()  # Asigna el nuevo UserManager

    TIPO_CHOICES = (
        ('cliente', 'Cliente'),
        ('profesional', 'Profesional'),
        ('admin', 'Admin'),
    )

    tipo_usuario = models.CharField(max_length=20, choices=TIPO_CHOICES, default='cliente')

    def __str__(self):
        return self.email


class Professional(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='datos_profesional')
    especiality = models.ManyToManyField('Servicios.Servicios', blank=True)
    experience = models.PositiveBigIntegerField(default=0)
    certificaciones = models.TextField(blank=True)
    disponibilidad_horaria = models.JSONField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profesionales/', blank=True, null=True)

    def __str__(self):
        return f'Profesional: {self.user.email}'