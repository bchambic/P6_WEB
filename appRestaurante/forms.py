from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(
        label="Usuario",
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su usuario'
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Ingrese su contraseña'
        }),
        required=True
    )
    
class PlatoForm(forms.Form):
    descripcion = forms.CharField(label="Descripción", max_length=200, required=True)
    precio = forms.DecimalField(label="Precio", max_digits=10, decimal_places=2, required=True)
    categoria = forms.CharField(label="Categoría", max_length=100, required=True)
    disponible = forms.BooleanField(label="Disponible", required=False, initial=True)

class MesaForm(forms.Form):
    estado = forms.CharField(label="Estado", max_length=50, required=True)
    ubicacion = forms.CharField(label="Ubicación", max_length=100, required=True)

class PedidoForm(forms.Form):
    estadoped = forms.CharField(label="Estado del Pedido", max_length=50, required=True)
    cliente = forms.CharField(label="Cliente", max_length=150, required=True)
    fecha = forms.DateField(label="Fecha", required=True)
    hora = forms.TimeField(label="Hora", required=True)
    notas = forms.CharField(label="Notas", widget=forms.Textarea, required=False)
    id_mesa = forms.IntegerField(label="ID Mesa", required=True)

class DetallePedidoForm(forms.Form):
    id_plato = forms.IntegerField(label="ID Plato", required=True)
    id_pedido = forms.IntegerField(label="ID Pedido", required=True)
    cantidad = forms.IntegerField(label="Cantidad", required=True)
    subtotal = forms.DecimalField(label="Subtotal", max_digits=10, decimal_places=2, required=True)
    
    
class PedidoMesaForm(forms.Form):
    id_mesa = forms.ChoiceField(
        label="Seleccionar Mesa",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cliente = forms.CharField(
        label="Cliente",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    notas = forms.CharField(
        label="Notas del Pedido",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    
    def __init__(self, *args, **kwargs):
        super(PedidoMesaForm, self).__init__(*args, **kwargs)
        # Obtener mesas disponibles para el dropdown
        from .models import Mesa
        mesas_disponibles = Mesa.objects.filter(estado='Disponible')
        choices = [(mesa.id_mesa, f"Mesa {mesa.id_mesa} - {mesa.ubicacion}") for mesa in mesas_disponibles]
        self.fields['id_mesa'].choices = [('', '-- Seleccione una mesa --')] + choices