from djongo import models

class Evento(models.Model):
    operacion = models.CharField(max_length=100, default='')
    descripcion = models.CharField(max_length=300, default='')
    fecha_hora = models.DateTimeField(auto_now=False)
