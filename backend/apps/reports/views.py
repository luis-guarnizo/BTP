from django.db.models import Count, F, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Student
from apps.accounts.permissions import IsReceptionistOrAdmin
from apps.attendance.models import CheckIn
from apps.notifications.models import NotificationLog
from apps.packages.models import Package


class RevenueReportView(APIView):
    """Ingresos por mes y por categoría (social / líneas)."""

    permission_classes = [IsReceptionistOrAdmin]

    def get(self, request):
        qs = (
            Package.objects.annotate(month=TruncMonth("purchase_date"))
            .values("month", "package_type__category")
            .annotate(total=Sum("package_type__price"), sales=Count("id"))
            .order_by("-month")
        )
        return Response(list(qs))


class ActiveStudentsReportView(APIView):
    """Alumnos activos vs. en mora (según su paquete más reciente)."""

    permission_classes = [IsReceptionistOrAdmin]

    def get(self, request):
        today = timezone.localdate()
        result = {"activos": 0, "vencidos": 0, "agotados": 0, "sin_paquete": 0, "por_categoria": {}}

        for student in Student.objects.filter(is_active=True).select_related():
            package = student.active_package()
            if package is None:
                result["sin_paquete"] += 1
                continue
            result[
                {"activo": "activos", "vencido": "vencidos", "agotado": "agotados"}[package.status]
            ] += 1

        result["total_alumnos"] = Student.objects.filter(is_active=True).count()
        result["por_categoria"] = dict(
            Student.objects.filter(is_active=True)
            .values_list("category")
            .annotate(count=Count("id"))
        )
        return Response(result)


class AttendanceReportView(APIView):
    """Asistencia por clase (para saber cuáles son las clases más populares)."""

    permission_classes = [IsReceptionistOrAdmin]

    def get(self, request):
        qs = (
            CheckIn.objects.values(name=F("class_offering__name"))
            .annotate(total_asistencias=Count("id"))
            .order_by("-total_asistencias")
        )
        return Response(list(qs))


class PendingAlertsView(APIView):
    """
    Lo que recepción necesita ver cada día: a quién cobrarle clase
    suelta o pedirle que renueve el paquete/mensualidad.
    """

    permission_classes = [IsReceptionistOrAdmin]

    def get(self, request):
        alerts = NotificationLog.objects.filter(
            channel=NotificationLog.CHANNEL_INTERNAL, resolved_at__isnull=True
        ).select_related("student", "package__package_type").order_by("-sent_at")
        data = [
            {
                "id": a.id,
                "student": str(a.student),
                "student_id": a.student_id,
                "type": a.get_notif_type_display(),
                "message": a.message,
                "sent_at": a.sent_at,
            }
            for a in alerts
        ]
        return Response(data)


class ResolveAlertView(APIView):
    """Recepción marca una alerta como atendida (ya cobró/renovó)."""

    permission_classes = [IsReceptionistOrAdmin]

    def post(self, request, pk):
        alert = get_object_or_404(NotificationLog, pk=pk, channel=NotificationLog.CHANNEL_INTERNAL)
        if alert.resolved_at is None:
            alert.resolved_at = timezone.now()
            alert.resolved_by = request.user
            alert.save(update_fields=["resolved_at", "resolved_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
