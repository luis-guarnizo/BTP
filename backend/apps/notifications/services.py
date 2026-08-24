from django.core.mail import send_mail
from django.conf import settings

from apps.notifications.models import NotificationLog


def notify_low_credit_email(package):
    """Manda un correo al alumno cuando le queda 1 clase de su paquete
    social. Se envía una sola vez por paquete."""
    student = package.student
    already_sent = NotificationLog.objects.filter(
        package=package, notif_type=NotificationLog.TYPE_LOW_CREDIT
    ).exists()
    if already_sent or not student.email:
        return None

    subject = "Te queda 1 clase en tu paquete"
    message = (
        f"Hola {student.first_name}, te queda 1 clase disponible en tu paquete "
        f"\"{package.package_type.name}\". Recuerda pasar por recepción para "
        f"renovarlo y no quedarte sin cupo."
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [student.email],
        fail_silently=True,
    )
    return NotificationLog.objects.create(
        student=student,
        package=package,
        notif_type=NotificationLog.TYPE_LOW_CREDIT,
        channel=NotificationLog.CHANNEL_EMAIL,
        message=message,
    )


def flag_receptionist(student, package, notif_type):
    """Crea una alerta interna (visible en el dashboard de recepción)
    para que actualicen el paquete o cobren la clase suelta. Evita
    duplicar la misma alerta sin resolver para el mismo paquete."""
    existing = NotificationLog.objects.filter(
        student=student,
        package=package,
        notif_type=notif_type,
        resolved_at__isnull=True,
    ).exists()
    if existing:
        return None

    label = dict(NotificationLog.TYPE_CHOICES).get(notif_type, notif_type)
    message = f"{student} - {label}"
    if package:
        message += f" (paquete: {package.package_type.name}, vence {package.expires_at})"

    return NotificationLog.objects.create(
        student=student,
        package=package,
        notif_type=notif_type,
        channel=NotificationLog.CHANNEL_INTERNAL,
        message=message,
    )
