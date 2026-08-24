from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from apps.accounts.models import Student
from apps.packages.models import PackageType

SOCIAL_PLANS = [
    ("1 clase", 25000, 1),
    ("4 clases", 80000, 4),
    ("6 clases", 120000, 6),
    ("8 clases", 200000, 8),
]

LINEAS_PLANS = [
    ("Kids", 120000),
    ("Amateur", 120000),
    ("Semipro", 110000),
    ("Profesional", 95000),
]


class Command(BaseCommand):
    """Crea el catálogo de paquetes/mensualidades y el grupo de
    Recepcionista. Se puede correr varias veces sin duplicar nada."""

    help = "Carga los planes de precios iniciales y el grupo 'Recepcionista'."

    def handle(self, *args, **options):
        Group.objects.get_or_create(name="Recepcionista")

        for name, price, credits in SOCIAL_PLANS:
            PackageType.objects.get_or_create(
                name=name,
                category=Student.CATEGORY_SOCIAL,
                defaults={"price": price, "credit_count": credits},
            )

        for name, price in LINEAS_PLANS:
            PackageType.objects.get_or_create(
                name=name,
                category=Student.CATEGORY_LINEAS,
                defaults={"price": price, "credit_count": None},
            )

        self.stdout.write(self.style.SUCCESS("Catálogo de paquetes y grupo Recepcionista listos."))
