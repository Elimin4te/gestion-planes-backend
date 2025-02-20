from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from autenticacion_docente.serializers import SerializadorDocente, SerializadorInicioSesion
from autenticacion_docente.permissions import CedulaRequerida
from autenticacion_docente.models import Docente

from django.conf import settings


class IniciarSesion(APIView):
    """Controlador para la autenticación docente."""
    permission_classes = [AllowAny]
    serializer_class = SerializadorInicioSesion

    def post(self, request):
        serializador = SerializadorInicioSesion(data=request.data)
        if serializador.is_valid():

            # Guardar la cedula en una cookie
            response = Response(status=202)
            response.set_cookie(settings.NOMBRE_COOKIE_DOCENTE, serializador.docente.cedula, httponly=True)

            return response

        else:
            # Devuelve la respuesta con los errores detectados.
            return Response(serializador.errors, status=400)


class ObtenerDatosDocente(APIView):
    """Controlador para mostrar datos de docente."""

    def get(self, request):
        cedula: str = request.COOKIES.get(settings.NOMBRE_COOKIE_DOCENTE)
        docente = Docente.objects.get(cedula=cedula)
        docente = SerializadorDocente(docente)
        return Response(docente.data)



class CerrarSesion(APIView):
    """Controlador para eliminar cookie de docente."""

    def get(self, request):
        response = Response(status=202)
        response.delete_cookie(settings.NOMBRE_COOKIE_DOCENTE)
        return response
