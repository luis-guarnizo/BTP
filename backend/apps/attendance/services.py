from django.conf import settings
from django.core.exceptions import ValidationError

from apps.attendance.models import CheckIn
from apps.notifications.models import NotificationLog
from apps.notifications.services import flag_receptionist, notify_low_credit_email
from apps.packages.models import Package


class CheckinBlocked(Exception):
    """Raised when a student can't be checked in. `reason` is a short
    machine-readable code the frontend can use to show a message."""

    def __init__(self, reason: str, message: str):
        self.reason = reason
        self.message = message
        super().__init__(message)


def perform_checkin(student, class_offering) -> CheckIn:
    package = student.active_package()

    if package is None:
        flag_receptionist(student, None, NotificationLog.TYPE_PACKAGE_EXHAUSTED)
        raise CheckinBlocked(
            "no_package",
            "No tienes un paquete o mensualidad activa. Pasa por recepción.",
        )

    if package.is_expired:
        notif_type = NotificationLog.TYPE_PACKAGE_EXPIRED
        flag_receptionist(student, package, notif_type)
        raise CheckinBlocked(
            "expired",
            "Tu paquete/mensualidad venció. Pasa por recepción para renovarlo.",
        )

    if package.is_exhausted:
        flag_receptionist(student, package, NotificationLog.TYPE_PACKAGE_EXHAUSTED)
        raise CheckinBlocked(
            "exhausted",
            "Ya usaste todas las clases de tu paquete. Pasa por recepción para "
            "renovar o pagar la clase suelta.",
        )

    will_deduct_credit = package.credits_remaining is not None

    checkin = CheckIn.objects.create(
        student=student,
        class_offering=class_offering,
        package=package,
        credit_deducted=will_deduct_credit,
    )

    if will_deduct_credit:
        package.consume_credit()
        if package.credits_remaining == settings.LOW_CREDIT_ALERT_THRESHOLD:
            notify_low_credit_email(package)
        elif package.credits_remaining <= 0:
            flag_receptionist(student, package, NotificationLog.TYPE_PACKAGE_EXHAUSTED)

    return checkin
