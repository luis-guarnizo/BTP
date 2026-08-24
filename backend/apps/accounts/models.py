from django.contrib.auth.hashers import check_password, make_password
from django.db import models


class Student(models.Model):
    """
    An alumno of the school. Not a Django `User` on purpose: students
    never touch the Django admin, they only authenticate through the
    lightweight phone+PIN check-in flow (see apps.accounts.views).

    Staff (dueño/recepcionista) instead use the normal Django auth
    `User` model + Groups, managed through the admin site.
    """

    CATEGORY_SOCIAL = "social"
    CATEGORY_LINEAS = "lineas"
    CATEGORY_CHOICES = [
        (CATEGORY_SOCIAL, "Social"),
        (CATEGORY_LINEAS, "Líneas (artístico)"),
    ]

    first_name = models.CharField("nombres", max_length=100)
    last_name = models.CharField("apellidos", max_length=100)
    phone = models.CharField("teléfono", max_length=20, unique=True)
    email = models.EmailField("correo", blank=True)
    document_id = models.CharField("cédula", max_length=30, blank=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    pin_hash = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # who registered this student (recepcionista), for auditing
    registered_by = models.ForeignKey(
        "auth.User", null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = "Alumno"
        verbose_name_plural = "Alumnos"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_category_display()})"

    def set_pin(self, raw_pin: str):
        self.pin_hash = make_password(raw_pin)

    def check_pin(self, raw_pin: str) -> bool:
        return check_password(raw_pin, self.pin_hash)

    def active_package(self):
        """Returns the student's currently usable package, if any."""
        from apps.packages.models import Package

        return (
            Package.objects.filter(student=self)
            .order_by("-purchase_date")
            .first()
        )
