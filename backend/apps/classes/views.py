from rest_framework import generics, permissions

from apps.accounts.permissions import IsReceptionistOrAdmin
from apps.classes.models import ClassOffering
from apps.classes.serializers import ClassOfferingSerializer


class TodayClassesView(generics.ListAPIView):
    """
    Lista de clases de hoy para que el alumno elija a cuál asistió al
    hacer check-in (paso 2 del flujo, ya con sesión iniciada).
    Público (no requiere ser recepción) porque lo usa la pantalla de
    check-in del alumno.
    """

    serializer_class = ClassOfferingSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return ClassOffering.today()


class ClassOfferingListCreateView(generics.ListCreateAPIView):
    """Administración del horario semanal (dueño/recepción)."""

    queryset = ClassOffering.objects.all()
    serializer_class = ClassOfferingSerializer
    permission_classes = [IsReceptionistOrAdmin]


class ClassOfferingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClassOffering.objects.all()
    serializer_class = ClassOfferingSerializer
    permission_classes = [IsReceptionistOrAdmin]
