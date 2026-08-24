from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsReceptionistOrAdmin, get_current_student
from apps.attendance.models import CheckIn
from apps.attendance.serializers import (
    CheckInRequestSerializer,
    CheckInResultSerializer,
)
from apps.attendance.services import CheckinBlocked, perform_checkin
from apps.classes.models import ClassOffering


class CheckInView(APIView):
    """
    Paso 2 del flujo de auto check-in: con la sesión ya iniciada
    (ver apps.accounts.CheckinLoginView), el alumno elige la clase a la
    que está entrando y el sistema descuenta el crédito (social) o solo
    registra la asistencia (líneas).
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        student = get_current_student(request)  # raises 401 if no session

        serializer = CheckInRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            class_offering = ClassOffering.objects.get(
                pk=serializer.validated_data["class_offering_id"], is_active=True
            )
        except ClassOffering.DoesNotExist:
            return Response(
                {"detail": "Clase no encontrada."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            checkin = perform_checkin(student, class_offering)
        except CheckinBlocked as exc:
            return Response(
                {"detail": exc.message, "reason": exc.reason},
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )

        return Response(CheckInResultSerializer(checkin).data, status=status.HTTP_201_CREATED)


class CheckInListView(generics.ListAPIView):
    """Historial de asistencias (recepción / reportes)."""

    queryset = CheckIn.objects.select_related("student", "class_offering", "package")
    serializer_class = CheckInResultSerializer
    permission_classes = [IsReceptionistOrAdmin]
