from django.db import models

class Plato(models.Model):
    id_plato = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=100)
    disponible = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'plato'

class Mesa(models.Model):
    id_mesa = models.AutoField(primary_key=True)
    estado = models.CharField(max_length=50)
    ubicacion = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'mesa'

class Pedido(models.Model):
    id_pedido = models.AutoField(primary_key=True)
    estadoped = models.CharField(max_length=50)
    cliente = models.CharField(max_length=150)
    fecha = models.DateField()
    hora = models.TimeField()
    notas = models.TextField(blank=True, null=True)
    id_mesa = models.ForeignKey(
        Mesa,
        on_delete=models.CASCADE,
        db_column='id_mesa'
    )

    class Meta:
        managed = False
        db_table = 'pedido'

class DetallePedido(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    id_plato = models.ForeignKey(
        Plato,
        on_delete=models.CASCADE,
        db_column='id_plato'
    )
    id_pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        db_column='id_pedido'
    )
    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'detallepedido'
        unique_together = (('id_plato', 'id_pedido'),)