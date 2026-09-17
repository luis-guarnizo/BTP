from datetime import date

from django.core.management.base import BaseCommand

from apps.accounts.models import Student
from apps.packages.models import Package

# Todos los alumnos de Líneas se registraron el mismo día de arranque de
# esta línea; se fija el ciclo real acordado (no el que calculó el
# sistema al crearse el registro el mismo día para todos).
LINEAS_PURCHASE_DATE = date(2026, 9, 5)
LINEAS_EXPIRES_AT = date(2026, 10, 5)


class Command(BaseCommand):
    """Corrige las fechas de los paquetes del registro inicial masivo de
    la academia (todos se crearon el mismo día, así que `purchase_date`
    no reflejaba la fecha real de pago de cada alumno).

    - Social: recalcula `expires_at` a partir de la `purchase_date` que ya
      se corrigió manualmente por alumno (mismo cálculo que usa el modelo
      al crear un paquete: compra + SOCIAL_PACKAGE_VALIDITY_DAYS). No
      toca `purchase_date`.
    - Líneas (artístico): fija compra=2026-09-05 y vence=2026-10-05 para
      TODOS los paquetes de alumnos de esa categoría, sin excepción.

    Pensado para correr una sola vez desde el Build Command de Render y
    luego quitarlo (a diferencia de import_students, este no es para
    dejar corriendo en cada deploy).
    """

    help = "Corrige fechas de compra/vencimiento del registro inicial de paquetes."

    def handle(self, *args, **options):
        social_qs = Package.objects.filter(
            student__category=Student.CATEGORY_SOCIAL
        ).select_related("package_type", "student")

        updated_social = 0
        for pkg in social_qs:
            new_expiry = pkg._compute_expiry()
            if pkg.expires_at != new_expiry:
                pkg.expires_at = new_expiry
                pkg.save(update_fields=["expires_at"])
                updated_social += 1
                self.stdout.write(
                    f"Social: {pkg.student} -> compra {pkg.purchase_date}, vence {new_expiry}"
                )

        lineas_updated = Package.objects.filter(
            student__category=Student.CATEGORY_LINEAS
        ).update(purchase_date=LINEAS_PURCHASE_DATE, expires_at=LINEAS_EXPIRES_AT)

        self.stdout.write(
            self.style.SUCCESS(
                f"Listo. Social: {updated_social} paquetes recalculados. "
                f"Líneas: {lineas_updated} paquetes fijados a "
                f"{LINEAS_PURCHASE_DATE} -> {LINEAS_EXPIRES_AT}."
            )
        )
