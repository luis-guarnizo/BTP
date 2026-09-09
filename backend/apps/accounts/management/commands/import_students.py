from django.core.management.base import BaseCommand

from apps.accounts.models import Student

# Listados de alumnos digitalizados desde registros en papel.
# (first_name, last_name, phone)

# "Línea 3 Amateur", "Línea 2 Semiprofesional", "Línea 1 Profesional".
LINEAS_STUDENTS = [
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
    # Listado "Línea 1 Profesional" digitalizado desde registro en papel,
    # agregado el 2026-09-09. Luis Miguel Espinosa no tenía número, así
    # que no se incluye aquí. Gabriela Rodríguez no venía en esta lista,
    # se agregó a mano por pedido directo.
    ("Juan José", "Rivas", "3122458012"),
    ("Alejandro", "López", "3171665459"),
    ("Kevin", "Tapasco", "3112225923"),
    ("Sebastián", "Martínez", "3025695934"),
    ("Stefanía", "Madrigal", "3234967897"),
    ("Angie", "Aldana", "3106775069"),
    ("Flora", "Rivera", "3023782368"),
    ("Gabriela", "Toro", "3176757302"),
    ("Stiven", "Ojeda", "3007709683"),
    ("Geraldine", "Londoño", "3105353050"),
    ("Saray", "Vargas", "3226538415"),
    ("Nicole", "Grajales", "3233273396"),
    ("Álvaro", "Tovar", "3185694620"),
    ("Bianca", "Torres", "3164996628"),
    ("Camilo", "Hernández", "3186142315"),
    ("Valentina", "Perea", "3058023920"),
    ("Juliana", "Quintero", "3182691328"),
    ("Mayra Alejandra", "Hoyos", "3012719292"),
    ("Sara", "Perdomo", "3163210629"),
    ("Antony", "Jordán", "3005863363"),
    ("Jacobo", "Lenis", "3135681370"),
    ("Gabriela", "Rodríguez", "3165049012"),
]

# "Iniciación Nivel 1" y "Nivel 2 Intermedio", agregado 2026-09-09.
# Oliver y Diana no traían apellido en la libreta; se guarda "Pendiente"
# como apellido temporal a pedido directo.
SOCIAL_STUDENTS = [
    ("Yerlin Viviana", "Losso", "3178037096"),
    ("Jhonier", "Solarte", "3161589340"),
    ("Juliana", "Dristizobol", "3102840236"),
    ("Eduar", "Llantén", "3235991296"),
    ("Tania", "Torrico", "3106560172"),
    ("Andrés", "Cañón", "3216775261"),
    ("Kevin", "Quiroz", "3165551614"),
    ("Sergio", "Camayo", "3226167226"),
    ("Daniel", "Suárez", "3128656975"),
    ("Lorena", "Erazo", "3122361839"),
    ("Samuel", "Solarte", "3024413331"),
    ("Paula", "Solarte", "3113960374"),
    ("Laura Viviana", "Ramírez", "3226657697"),
    ("Oliver", "Pendiente", "3146487641"),
    ("Diana", "Pendiente", "3148297908"),
    ("Víctor", "Cañón", "3235091859"),
    ("Julián", "Murcia", "3017900352"),
]


class Command(BaseCommand):
    """Importa los listados de alumnos digitalizados desde registros en
    papel (varias líneas artísticas y niveles de social). Idempotente por
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

        batches = [
            (LINEAS_STUDENTS, Student.CATEGORY_LINEAS),
            (SOCIAL_STUDENTS, Student.CATEGORY_SOCIAL),
        ]
        for students, category in batches:
            for first_name, last_name, phone in students:
                if Student.objects.filter(phone=phone).exists():
                    self.stdout.write(f"Ya existe, se omite: {first_name} {last_name} ({phone})")
                    skipped += 1
                    continue
                student = Student(
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    category=category,
                )
                student.set_pin(phone[-4:])
                student.save()
                created += 1
                self.stdout.write(f"Creado: {first_name} {last_name} ({phone})")

        self.stdout.write(
            self.style.SUCCESS(f"Listo: {created} alumnos creados, {skipped} ya existían.")
        )
