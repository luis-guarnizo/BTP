from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission

STUDENT_SESSION_KEY = "student_id"


def get_current_student(request):
    """
    Returns the Student tied to this browser session (set at
    /api/accounts/checkin-login/), or raises 401 if there isn't one.
    Used by the self-service check-in endpoints, which intentionally
    don't use Django's staff auth.
    """
    from apps.accounts.models import Student

    student_id = request.session.get(STUDENT_SESSION_KEY)
    if not student_id:
        raise AuthenticationFailed("Debes iniciar sesión para registrar tu asistencia.")
    try:
        return Student.objects.get(pk=student_id, is_active=True)
    except Student.DoesNotExist as exc:
        request.session.pop(STUDENT_SESSION_KEY, None)
        raise AuthenticationFailed("Tu sesión ya no es válida, ingresa de nuevo.") from exc


def is_receptionist_or_admin(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return True
    return user.groups.filter(name="Recepcionista").exists()


class IsReceptionistOrAdmin(BasePermission):
    """DRF permission class for staff-only endpoints (registrar alumnos,
    vender/renovar paquetes, ver reportes)."""

    message = "No tienes permisos de recepción/administración."

    def has_permission(self, request, view):
        return is_receptionist_or_admin(request.user)
