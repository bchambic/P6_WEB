import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'G6_Proyecto_PWEB.settings')
django.setup()

from appRestaurante.models import UsuarioPersonalizado

# Crear usuarios iniciales
usuarios = [
    {'username': 'admin', 'password': 'password123', 'tipo': 'admin'},
    {'username': 'operador1', 'password': 'password123', 'tipo': 'operador'},
    {'username': 'operador2', 'password': 'password123', 'tipo': 'operador'},
]

for usuario_data in usuarios:
    if not UsuarioPersonalizado.objects.filter(username=usuario_data['username']).exists():
        usuario = UsuarioPersonalizado(
            username=usuario_data['username'],
            tipo_usuario=usuario_data['tipo']
        )
        usuario.set_password(usuario_data['password'])
        usuario.save()
        print(f"Usuario {usuario_data['username']} creado")

print("Usuarios creados exitosamente")