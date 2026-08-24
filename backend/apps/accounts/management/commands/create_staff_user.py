import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Crea (o actualiza la contraseña de) el usuario admin de recepción.

    Pensado para correr en el build command de producción (Render no
    incluye acceso a shell en el plan gratuito), leyendo las credenciales
    de variables de entorno en vez de pedirlas por consola.
    """

    help = "Crea el superusuario de staff a partir de ADMIN_USERNAME/ADMIN_PASSWORD."

    def handle(self, *args, **options):
        username = os.getenv("ADMIN_USERNAME")
        password = os.getenv("ADMIN_PASSWORD")
        email = os.getenv("ADMIN_EMAIL", "")

        if not username or not password:
            self.stdout.write("ADMIN_USERNAME/ADMIN_PASSWORD no configurados, se omite.")
            return

        user, created = User.objects.get_or_create(
            username=username, defaults={"email": email}
        )
        user.email = email or user.email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        self.stdout.write(
            self.style.SUCCESS(f"Usuario admin {'creado' if created else 'actualizado'}: {username}")
        )
