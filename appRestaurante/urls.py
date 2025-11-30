from django.urls import path
from . import views

urlpatterns = [
    # URLs existentes...
    path('platos/', views.listar_platos, name='listar_platos'),
    path('platos/nuevo/', views.crear_plato, name='crear_plato'),
    path('platos/actualizar/<int:id>/', views.actualizar_plato, name='actualizar_plato'),
    path('platos/eliminar/<int:id>/', views.eliminar_plato, name='eliminar_plato'),
    
    path('mesas/', views.listar_mesas, name='listar_mesas'),
    path('mesas/nuevo/', views.crear_mesa, name='crear_mesa'),
    path('mesas/actualizar/<int:id>/', views.actualizar_mesa, name='actualizar_mesa'),
    path('mesas/eliminar/<int:id>/', views.eliminar_mesa, name='eliminar_mesa'),
    
    path('pedidos/', views.listar_pedidos, name='listar_pedidos'),
    path('pedidos/nuevo/', views.crear_pedido, name='crear_pedido'),
    path('pedidos/actualizar/<int:id>/', views.actualizar_pedido, name='actualizar_pedido'),
    path('pedidos/eliminar/<int:id>/', views.eliminar_pedido, name='eliminar_pedido'),
    
    path('detalles-pedido/', views.listar_detalles_pedido, name='listar_detalles_pedido'),
    path('detalles-pedido/nuevo/', views.crear_detalle_pedido, name='crear_detalle_pedido'),
    path('detalles-pedido/eliminar/<int:id_plato>/<int:id_pedido>/', views.eliminar_detalle_pedido, name='eliminar_detalle_pedido'),
    
    # NUEVAS RUTAS PARA LAS FUNCIONALIDADES ESPECÍFICAS
    path('tomar-pedido/', views.tomar_pedido_mesa, name='tomar_pedido'),
    path('seleccionar-platos/<int:id_pedido>/', views.seleccionar_platos, name='seleccionar_platos'),
    path('reporte-ventas/', views.reporte_ventas_platos, name='reporte_ventas'),
    path('actualizar-estado/<int:id_pedido>/', views.actualizar_estado_pedido, name='actualizar_estado'),
    
    # URLs de autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('', views.index, name='index'),
]