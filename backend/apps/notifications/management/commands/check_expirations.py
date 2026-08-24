from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.notifications.models import NotificationLog
from apps.notifications.services import flag_receptionist
from apps.packages.models import Package


class Command(BaseCommand):
    """
    Corre diario (cron) para detectar paquetes/mensualidades vencidas
    que el alumno nunca intentó usar (por lo que el check-in nunca
    generó la alerta) y avisar a recepción de todas formas.

    Programar, por ejemplo en Render/Railway: `python manage.py check_expirations`
    una vez al día.
    """

    help = "Revisa paquetes vencidos/agotados y crea alertas para recepción."

    def handle(self, *args, **options):
        today = timezone.localdate()
        expired_packages = Package.objects.filter(expires_at__lt=today).select_related(
            "student", "package_type"
        )

        created = 0
        for package in expired_packages:
            # Only the most recent package per student matters (older,
            # already-replaced packages shouldn't keep alerting).
            if package != package.student.active_package():
                continue
            alert = flag_receptionist(
                package.student, package, NotificationLog.TYPE_PACKAGE_EXPIRED
            )
            if alert:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Alertas de vencimiento creadas: {created}"))
