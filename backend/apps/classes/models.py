from django.db import models
from django.utils import timezone


class ClassOffering(models.Model):
    """
    A recurring class/session in the weekly schedule (e.g. "Salsa -
    martes 6pm"). Alumnos pueden asistir a cualquiera sin importar su
    paquete. `room` is kept as a field (not hardcoded) so adding a
    second salón later doesn't require a schema change.
    """

    WEEKDAY_CHOICES = [
        (0, "Lunes"),
        (1, "Martes"),
        (2, "Miércoles"),
        (3, "Jueves"),
        (4, "Viernes"),
        (5, "Sábado"),
        (6, "Domingo"),
    ]

    name = models.CharField(max_length=100, help_text="Ej: Salsa, Bachata, Kids, Amateur...")
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=100, default="Salón principal")
    instructor_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Clase"
        verbose_name_plural = "Clases (horario)"
        ordering = ["weekday", "start_time"]

    def __str__(self):
        return f"{self.name} - {self.get_weekday_display()} {self.start_time:%H:%M}"

    @classmethod
    def today(cls):
        weekday = timezone.localtime().weekday()
        return cls.objects.filter(weekday=weekday, is_active=True).order_by("start_time")
