from django.core.management.base import BaseCommand

from apps.accounts.models import Student

# Listado "Línea 3 Amateur" digitalizado desde registro en papel.
# (first_name, last_name, phone)
STUDENTS = [
    ("Laura Sofía", "", "3150400409"),
    ("Dominik", "Ordóñez", "3005913049"),
    ("María", "Parra", "3188332268"),
    ("Julián", "Torres", "3216187392"),
    ("Valentina", "Paredes", "3116966107"),
    ("Isabella", "Rosero", "3128193900"),
    ("Isabel", "Gutiérrez V.", "3127529365"),
    ("Sebastián", "Monzón", "3206134806"),
    ("Sara", "Obando", "3178107629"),
    ("Tyler", "Gutiérrez", "3234731369"),
    ("Luis Ángel", "Cotaño", "3174863638"),
    ("Natalia", "Garcés", "3197038780"),
    ("María Alejandra", "Cortés", "3176695091"),
]


class Command(BaseCommand):
    """Importa el listado inicial de alumnos de 'Línea 3 Amateur' (registro
    en papel, digitalizado el 2026-09-09). Idempotente por teléfono: si ya
    existe un alumno con ese número, se omite sin pisar datos existentes.

    PIN inicial = últimos 4 dígitos del teléfono; el alumno lo puede
    cambiar después desde el check-in.

    Pensado para correr una sola vez desde el Build Command de Render
    (plan free no tiene shell) y luego quitarlo del Build Command.
    """

    help = "Importa el listado inicial de alumnos de Línea 3 Amateur."

    def handle(self, *args, **options):
        created = 0
        skipped = 0
        for first_name, last_name, phone in STUDENTS:
            if Student.objects.filter(phone=phone).exists():
                self.stdout.write(f"Ya existe, se omite: {first_name} {last_name} ({phone})")
                skipped += 1
                continue
            student = Student(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                category=Student.CATEGORY_LINEAS,
            )
            student.set_pin(phone[-4:])
            student.save()
            created += 1
            self.stdout.write(f"Creado: {first_name} {last_name} ({phone})")

        self.stdout.write(
            self.style.SUCCESS(f"Listo: {created} alumnos creados, {skipped} ya existían.")
        )
