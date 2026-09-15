from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Student
from apps.accounts.permissions import (
    STUDENT_SESSION_KEY,
    IsReceptionistOrAdmin,
    get_current_student,
    is_receptionist_or_admin,
)
from apps.accounts.serializers import (
    StudentLoginSerializer,
    StudentPublicSerializer,
    StudentRegisterSerializer,
)


@method_decorator(ensure_csrf_cookie, name="get")
class CsrfCookieView(APIView):
    """
    El dashboard de recepción (React) llama esto una vez al cargar para
    recibir la cookie `csrftoken`. Django exige ese token en el header
    `X-CSRFToken` en cada POST/PUT/DELETE hecho con sesión de staff
    (no aplica a los alumnos, que no usan auth de Django).
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"csrfToken": get_token(request)})


class StaffLoginView(APIView):
    """Login para dueño/recepcionista (dashboard de React)."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username", "").strip()
        password = request.data.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is None or not is_receptionist_or_admin(user):
            return Response(
                {"detail": "Usuario o contraseña incorrectos."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        login(request, user)
        return Response(
            {
                "username": user.username,
                "is_superuser": user.is_superuser,
                "is_staff": user.is_staff,
            }
        )


class StaffLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class StaffMeView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user = request.user
        if not is_receptionist_or_admin(user):
            return Response({"authenticated": False})
        return Response(
            {
                "authenticated": True,
                "username": user.username,
                "is_superuser": user.is_superuser,
            }
        )


class CheckinLoginView(APIView):
    """
    Paso 1 del flujo de auto check-in: el alumno escanea el QR físico
    fijo del salón, cae en esta pantalla la primera vez y se identifica
    con teléfono + PIN. La sesión queda guardada en su celular
    (cookie de larga duración) para que las próximas veces solo tenga
    que confirmar asistencia.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = StudentLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone"].strip()
        pin = serializer.validated_data["pin"].strip()

        try:
            student = Student.objects.get(phone=phone, is_active=True)
        except Student.DoesNotExist:
            return Response(
                {"detail": "Teléfono o PIN incorrectos."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not student.check_pin(pin):
            return Response(
                {"detail": "Teléfono o PIN incorrectos."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        request.session[STUDENT_SESSION_KEY] = student.id
        request.session.set_expiry(settings.STUDENT_SESSION_COOKIE_AGE)
        return Response(StudentPublicSerializer(student).data)


class CheckinLogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        request.session.pop(STUDENT_SESSION_KEY, None)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CheckinMeView(APIView):
    """Used by the check-in web page to know if the phone already has a
    valid session, and to show the student's current package status."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        try:
            student = get_current_student(request)
        except Exception:
            return Response({"authenticated": False})

        from apps.packages.serializers import PackageStatusSerializer

        package = student.active_package()
        return Response(
            {
                "authenticated": True,
                "student": StudentPublicSerializer(student).data,
                "package": PackageStatusSerializer(package).data if package else None,
            }
        )


class StudentListCreateView(generics.ListCreateAPIView):
    """Recepción: registrar alumnos nuevos / listar alumnos.

    Sin paginación: el frontend usa este listado completo para el
    selector de alumnos al vender un paquete y para la tabla de
    "Alumnos", así que siempre debe traer todos, no solo la primera
    página (con la paginación por defecto de 25, los alumnos importados
    después del #25 no aparecían en esas pantallas).
    """

    queryset = Student.objects.all().order_by("-created_at")
    permission_classes = [IsReceptionistOrAdmin]
    filterset_fields = ["category", "is_active"]
    pagination_class = None

    def get_serializer_class(self):
        if self.request.method == "POST":
            return StudentRegisterSerializer
        return StudentPublicSerializer


class StudentDetailView(generics.RetrieveUpdateAPIView):
    queryset = Student.objects.all()
    permission_classes = [IsReceptionistOrAdmin]
    serializer_class = StudentPublicSerializer
