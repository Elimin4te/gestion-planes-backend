from django.urls import path
from . import views

# Registro de URLs

urlpatterns = [
    path('login', views.IniciarSesion.as_view(), name='login-autenticacion-docente'), # Principal
    path('logout', views.CerrarSesion.as_view(), name='logout-autenticacion-docente'),
    path('info', views.ObtenerDatosDocente.as_view(), name='info-autenticacion-docente')
]