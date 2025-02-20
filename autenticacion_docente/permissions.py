from rest_framework.permissions import BasePermission
from django.conf import settings

from autenticacion_docente.models import Docente

class CedulaRequerida(BasePermission):
    """
    Permiso que requiere que la cookie 'cedula' esté presente en la petición.
    """

    message = f'Se requiere la cookie "{settings.NOMBRE_COOKIE_DOCENTE}" para acceder a este recurso.'

    def has_permission(self, request, view):
        """Valida que exista la cookie y que además la cédula del docente exista."""
        cedula: str | None = request.COOKIES.get(settings.NOMBRE_COOKIE_DOCENTE)

        if not cedula:
            return False

        return Docente.objects.filter(cedula=cedula).exists()

        