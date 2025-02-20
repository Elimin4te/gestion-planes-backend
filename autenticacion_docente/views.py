from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from autenticacion_docente.serializers import SerializadorDocente, SerializadorInicioSesion

from django.conf import settings


class IniciarSesion(APIView):
    """Controlador para la autenticación docente."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializador = SerializadorInicioSesion(data=request.data)
        if serializador.is_valid():

            # Obtener el docente desde el serializador ya validado
            docente = serializador.docente  

            # Serializar el objeto Docente
            docente_serializer = SerializadorDocente(docente)

            # Guardar la cedula en una cookie
            response = Response(docente_serializer.data)
            response.set_cookie(settings.NOMBRE_COOKIE_DOCENTE, docente.cedula, httponly=True)

            return response

        else:
            # Devuelve la respuesta con los errores detectados.
            return Response(serializador.errors, status=400)


class CerrarSesion(APIView):
    """Controlador para eliminar cookie de docente."""
    permission_classes = [AllowAny]

    def get(self, request):
        response = Response(status=202)
        response.delete_cookie(settings.NOMBRE_COOKIE_DOCENTE)
