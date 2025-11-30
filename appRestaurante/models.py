from django.db import models
import bcrypt

class UsuarioPersonalizado(models.Model):
    TIPO_USUARIO = [
        ('admin', 'Administrador'),
        ('operador', 'Operador'),
    ]
    
    id_usuario = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    password_hash = models.CharField(max_length=255)  # Para bcrypt
    tipo_usuario = models.CharField(max_length=10, choices=TIPO_USUARIO)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True  # Esta tabla SÍ la maneja Django
        db_table = 'usuarios'

    def set_password(self, password):
        # Usando bcrypt
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def __str__(self):
        return f"{self.username} ({self.tipo_usuario})"

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