from django.shortcuts import render, get_object_or_404, redirect
from .models import Plato, Mesa, Pedido, DetallePedido
from .forms import PlatoForm, MesaForm, PedidoForm, DetallePedidoForm, PedidoMesaForm
from django.db import transaction
from datetime import date, time
from django.db.models import Sum, Count
from decimal import Decimal
from datetime import datetime
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import UsuarioPersonalizado
from .forms import LoginForm

# VISTAS DE AUTENTICACIÓN
def login_view(request):
    # Si ya está logueado, redirigir según su tipo
    if 'user_id' in request.session:
        return redirect_por_tipo_usuario(request.session['tipo_usuario'])
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            try:
                usuario = UsuarioPersonalizado.objects.get(username=username, activo=True)
                if usuario.check_password(password):
                    # Crear sesión
                    request.session['user_id'] = usuario.id_usuario
                    request.session['username'] = usuario.username
                    request.session['tipo_usuario'] = usuario.tipo_usuario
                    request.session.set_expiry(3600)  # 1 hora
                    
                    messages.success(request, f'Bienvenido {usuario.username}')
                    return redirect_por_tipo_usuario(usuario.tipo_usuario)
                else:
                    messages.error(request, 'Contraseña incorrecta')
            except UsuarioPersonalizado.DoesNotExist:
                messages.error(request, 'Usuario no encontrado')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})

def redirect_por_tipo_usuario(tipo_usuario):
    # TODOS van al index, no importa el tipo de usuario
    return redirect('index')

def logout_view(request):
    # Limpiar sesión
    request.session.flush()
    messages.success(request, 'Sesión cerrada correctamente')
    return redirect('login')

# DECORATOR PERSONALIZADO PARA VERIFICAR LOGIN Y PERMISOS
def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'user_id' not in request.session:
            messages.error(request, 'Debe iniciar sesión para acceder')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'user_id' not in request.session:
            messages.error(request, 'Debe iniciar sesión para acceder')
            return redirect('login')
        if request.session.get('tipo_usuario') != 'admin':
            messages.error(request, 'No tiene permisos para acceder a esta sección')
            return redirect('tomar_pedido')
        return view_func(request, *args, **kwargs)
    return wrapper

def operador_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'user_id' not in request.session:
            messages.error(request, 'Debe iniciar sesión para acceder')
            return redirect('login')
        if request.session.get('tipo_usuario') not in ['admin', 'operador']:
            messages.error(request, 'No tiene permisos para acceder')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

# VISTAS PARA PLATO
@admin_required
def listar_platos(request):
    platos = Plato.objects.all()
    return render(request, 'listar_platos.html', {'platos': platos})
@admin_required
def crear_plato(request):
    if request.method == 'POST':
        form = PlatoForm(request.POST)
        if form.is_valid():
            Plato.objects.create(
                descripcion=form.cleaned_data['descripcion'],
                precio=form.cleaned_data['precio'],
                categoria=form.cleaned_data['categoria'],
                disponible=form.cleaned_data['disponible']
            )
            return redirect('listar_platos')
    else:
        form = PlatoForm()
    return render(request, 'nuevo_plato.html', {'form': form})
@admin_required
def actualizar_plato(request, id):
    plato = get_object_or_404(Plato, id_plato=id)
    if request.method == 'POST':
        form = PlatoForm(request.POST)
        if form.is_valid():
            plato.descripcion = form.cleaned_data['descripcion']
            plato.precio = form.cleaned_data['precio']
            plato.categoria = form.cleaned_data['categoria']
            plato.disponible = form.cleaned_data['disponible']
            plato.save()
            return redirect('listar_platos')
    else:
        form = PlatoForm(initial={
            'descripcion': plato.descripcion,
            'precio': plato.precio,
            'categoria': plato.categoria,
            'disponible': plato.disponible,
        })
    return render(request, 'actualizar_plato.html', {'form': form})
@admin_required
def eliminar_plato(request, id):
    plato = get_object_or_404(Plato, id_plato=id)
    plato.delete()
    return redirect('listar_platos')

# VISTAS PARA MESA
@admin_required
@operador_required
def listar_mesas(request):
    mesas = Mesa.objects.all()
    return render(request, 'listar_mesas.html', {'mesas': mesas})

@admin_required
def crear_mesa(request):
    if request.method == 'POST':
        form = MesaForm(request.POST)
        if form.is_valid():
            Mesa.objects.create(
                estado=form.cleaned_data['estado'],
                ubicacion=form.cleaned_data['ubicacion']
            )
            return redirect('listar_mesas')
    else:
        form = MesaForm()
    return render(request, 'nuevo_mesa.html', {'form': form})

@admin_required
@operador_required
def actualizar_mesa(request, id):
    mesa = get_object_or_404(Mesa, id_mesa=id)
    if request.method == 'POST':
        form = MesaForm(request.POST)
        if form.is_valid():
            mesa.estado = form.cleaned_data['estado']
            mesa.ubicacion = form.cleaned_data['ubicacion']
            mesa.save()
            return redirect('listar_mesas')
    else:
        form = MesaForm(initial={
            'estado': mesa.estado,
            'ubicacion': mesa.ubicacion,
        })
    return render(request, 'actualizar_mesa.html', {'form': form})

@admin_required
def eliminar_mesa(request, id):
    mesa = get_object_or_404(Mesa, id_mesa=id)
    mesa.delete()
    return redirect('listar_mesas')

# VISTAS PARA PEDIDO
@operador_required
def listar_pedidos(request):
    pedidos = Pedido.objects.all()
    return render(request, 'listar_pedidos.html', {'pedidos': pedidos})

@operador_required
def crear_pedido(request):
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            mesa = get_object_or_404(Mesa, id_mesa=form.cleaned_data['id_mesa'])
            Pedido.objects.create(
                estadoped=form.cleaned_data['estadoped'],
                cliente=form.cleaned_data['cliente'],
                fecha=form.cleaned_data['fecha'],
                hora=form.cleaned_data['hora'],
                notas=form.cleaned_data['notas'],
                id_mesa=mesa
            )
            return redirect('listar_pedidos')
    else:
        form = PedidoForm()
    return render(request, 'nuevo_pedido.html', {'form': form})

@operador_required
def actualizar_pedido(request, id):
    pedido = get_object_or_404(Pedido, id_pedido=id)
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            mesa = get_object_or_404(Mesa, id_mesa=form.cleaned_data['id_mesa'])
            pedido.estadoped = form.cleaned_data['estadoped']
            pedido.cliente = form.cleaned_data['cliente']
            pedido.fecha = form.cleaned_data['fecha']
            pedido.hora = form.cleaned_data['hora']
            pedido.notas = form.cleaned_data['notas']
            pedido.id_mesa = mesa
            pedido.save()
            return redirect('listar_pedidos')
    else:
        form = PedidoForm(initial={
            'estadoped': pedido.estadoped,
            'cliente': pedido.cliente,
            'fecha': pedido.fecha,
            'hora': pedido.hora,
            'notas': pedido.notas,
            'id_mesa': pedido.id_mesa.id_mesa,
        })
    return render(request, 'actualizar_pedido.html', {'form': form})

@operador_required
def eliminar_pedido(request, id):
    pedido = get_object_or_404(Pedido, id_pedido=id)
    pedido.delete()
    return redirect('listar_pedidos')
# VISTAS PARA DETALLE PEDIDO
@operador_required
def listar_detalles_pedido(request):
    detalles = DetallePedido.objects.all()
    return render(request, 'detalle_pedido.html', {'detalles': detalles})

@operador_required
def crear_detalle_pedido(request):
    if request.method == 'POST':
        form = DetallePedidoForm(request.POST)
        if form.is_valid():
            plato = get_object_or_404(Plato, id_plato=form.cleaned_data['id_plato'])
            pedido = get_object_or_404(Pedido, id_pedido=form.cleaned_data['id_pedido'])
            
            # Verificar si ya existe este detalle
            detalle_existente = DetallePedido.objects.filter(
                id_plato=plato, 
                id_pedido=pedido
            ).first()
            
            if detalle_existente:
                # Si existe, actualizar en lugar de crear
                detalle_existente.cantidad = form.cleaned_data['cantidad']
                detalle_existente.subtotal = form.cleaned_data['subtotal']
                detalle_existente.save()
            else:
                # Si no existe, crear nuevo
                DetallePedido.objects.create(
                    id_plato=plato,
                    id_pedido=pedido,
                    cantidad=form.cleaned_data['cantidad'],
                    subtotal=form.cleaned_data['subtotal']
                )
            return redirect('listar_detalles_pedido')
    else:
        form = DetallePedidoForm()
    return render(request, 'nuevo_detalle_pedido.html', {'form': form})

@operador_required
def eliminar_detalle_pedido(request, id_plato, id_pedido):
    detalle = get_object_or_404(
        DetallePedido, 
        id_plato=id_plato, 
        id_pedido=id_pedido
    )
    detalle.delete()
    return redirect('listar_detalles_pedido')

def index(request):
    return render(request, 'index.html')


# FUNCIONALIDAD 1: TOMAR PEDIDOS POR MESA
from django.db import connection
@operador_required
def tomar_pedido_mesa(request):
    if request.method == 'POST':
        form = PedidoMesaForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    mesa = get_object_or_404(Mesa, id_mesa=form.cleaned_data['id_mesa'])
                    
                    # INSERT DIRECTO EN SQL
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO pedido (estadoped, cliente, fecha, hora, notas, id_mesa) 
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, [
                            'Preparando',
                            form.cleaned_data['cliente'],
                            date.today(),
                            timezone.now().time(),
                            form.cleaned_data['notas'],
                            mesa.id_mesa
                        ])
                        
                        # Obtener el ID del pedido recién insertado
                        cursor.execute("SELECT LAST_INSERT_ID()")
                        id_pedido = cursor.fetchone()[0]
                    
                    mesa.estado = 'Ocupada'
                    mesa.save()
                    return redirect('seleccionar_platos', id_pedido=id_pedido)
                    
            except Exception as e:
                return render(request, 'tomar_pedido.html', {
                    'form': form,
                    'error': f'Error al crear el pedido: {str(e)}'
                })
    else:
        form = PedidoMesaForm()
    
    return render(request, 'tomar_pedido.html', {'form': form})

@operador_required
def seleccionar_platos(request, id_pedido):
    pedido = get_object_or_404(Pedido, id_pedido=id_pedido)
    platos = Plato.objects.filter(disponible=True)
    
    if request.method == 'POST':
        # Procesar los platos seleccionados
        platos_seleccionados = request.POST.getlist('platos')
        cantidades = request.POST.getlist('cantidades')
        
        for i, id_plato in enumerate(platos_seleccionados):
            if id_plato and cantidades[i]:
                try:
                    plato = Plato.objects.get(id_plato=id_plato)
                    cantidad = int(cantidades[i])
                    subtotal = plato.precio * cantidad
                    
                    # Crear detalle del pedido
                    DetallePedido.objects.create(
                        id_plato=plato,
                        id_pedido=pedido,
                        cantidad=cantidad,
                        subtotal=subtotal
                    )
                except (Plato.DoesNotExist, ValueError):
                    continue
        
        return redirect('listar_pedidos')
    
    return render(request, 'seleccionar_platos.html', {
        'pedido': pedido,
        'platos': platos
    })
    
    


# FUNCIONALIDAD 2: REPORTE DE VENTAS POR PLATO
@admin_required
def reporte_ventas_platos(request):
    # Obtener ventas agrupadas por plato
    ventas_por_plato = DetallePedido.objects.values(
        'id_plato__id_plato',
        'id_plato__descripcion',
        'id_plato__categoria'
    ).annotate(
        total_vendido=Sum('cantidad'),
        total_ingresos=Sum('subtotal'),
        veces_pedido=Count('id_pedido')
    ).order_by('-total_ingresos')
    
    # Calcular totales generales
    total_ingresos_general = sum(item['total_ingresos'] or Decimal('0') for item in ventas_por_plato)
    total_platos_vendidos = sum(item['total_vendido'] or 0 for item in ventas_por_plato)
    
    # Ventas por categoría
    ventas_por_categoria = DetallePedido.objects.values(
        'id_plato__categoria'
    ).annotate(
        total_ingresos=Sum('subtotal'),
        total_vendido=Sum('cantidad')
    ).order_by('-total_ingresos')
    
    return render(request, 'reporte_ventas.html', {
        'ventas_por_plato': ventas_por_plato,
        'ventas_por_categoria': ventas_por_categoria,
        'total_ingresos_general': total_ingresos_general,
        'total_platos_vendidos': total_platos_vendidos
    })
    
    
    # FUNCIONALIDAD 3: ACTUALIZAR ESTADO DEL PEDIDO
@operador_required
def actualizar_estado_pedido(request, id_pedido):
    pedido = get_object_or_404(Pedido, id_pedido=id_pedido)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        if nuevo_estado in ['Preparando', 'Entregado', 'Cancelado']:
            pedido.estadoped = nuevo_estado
            pedido.save()
            
            # Si el pedido se entrega o cancela, liberar la mesa
            if nuevo_estado in ['Entregado', 'Cancelado']:
                mesa = pedido.id_mesa
                mesa.estado = 'Disponible'
                mesa.save()
            
            return redirect('listar_pedidos')
    
    return render(request, 'actualizar_estado.html', {'pedido': pedido})

# PÁGINA PRINCIPAL REDIRIGE SEGÚN USUARIO
def index(request):
    # Si el usuario está logueado, mostrar el dashboard
    if 'user_id' in request.session:
        return render(request, 'index.html')
    else:
        # Si no está logueado, redirigir al login
        return redirect('login')