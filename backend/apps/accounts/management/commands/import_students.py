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
    # Listado "Línea 2 Semiprofesional" digitalizado desde registro en
    # papel, agregado el 2026-09-09. Valentina Paredes ya estaba en la
    # lista de arriba (mismo teléfono) y Emily Mosquera no tenía número,
    # así que no se incluyen aquí.
    ("Luis Gonzalo", "Guarnizo", "3185970857"),
    ("Melanie", "Cardona", "3107007082"),
    ("Alejandra", "Garcés", "3244549178"),
    ("Isabella", "Muñoz", "3115640007"),
    ("Mariana", "López", "3163321565"),
    ("Giovanny", "Cotaño", "3156281342"),
    ("Katherine", "Muñoz", "3158009573"),
    ("Sorya", "", "3243551046"),
    ("Luisa", "Arias", "3216642395"),
    ("Juan David", "Quintero G.", "3177814774"),
    ("Carolina", "Camayo", "3022905374"),
]


class Command(BaseCommand):
    """Importa los listados de alumnos digitalizados desde registros en
    papel ('Línea 3 Amateur', 'Línea 2 Semiprofesional'). Idempotente por
    teléfono: si ya existe un alumno con ese número, se omite sin pisar
    datos existentes.

    PIN inicial = últimos 4 dígitos del teléfono; el alumno lo puede
    cambiar después desde el check-in.

    Pensado para correr desde el Build Command de Render (plan free no
    tiene shell) cada vez que se digitaliza una lista nueva; es seguro
    dejarlo en el Build Command de forma permanente.
    """

    help = "Importa los listados de alumnos digitalizados desde papel."

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
