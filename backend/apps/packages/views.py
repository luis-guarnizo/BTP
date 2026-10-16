from rest_framework import generics
from rest_framework.response import Response

from apps.accounts.permissions import IsReceptionistOrAdmin
from apps.packages.models import Package, PackageType
from apps.packages.serializers import (
    PackageCreateSerializer,
    PackagePurchaseDateSerializer,
    PackageStatusSerializer,
    PackageTypeSerializer,
)


class PackageTypeListView(generics.ListAPIView):
    """Catálogo de planes (para mostrar precios en recepción/registro)."""

    queryset = PackageType.objects.filter(is_active=True)
    serializer_class = PackageTypeSerializer
    permission_classes = [IsReceptionistOrAdmin]


class PackageListCreateView(generics.ListCreateAPIView):
    """Recepción: vender/renovar un paquete o mensualidad a un alumno.

    Sin paginación: el frontend consume este listado completo en la tabla
    de "Últimos paquetes" sin manejar páginas, así que con la paginación
    por defecto (25) los paquetes más antiguos que la página 1 no
    aparecían.
    """

    queryset = Package.objects.select_related("student", "package_type").order_by(
        "-purchase_date", "-created_at"
    )
    permission_classes = [IsReceptionistOrAdmin]
    filterset_fields = ["student", "package_type__category"]
    pagination_class = None

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PackageCreateSerializer
        return PackageStatusSerializer


class PackageDetailView(generics.UpdateAPIView):
    """Recepción: corregir la fecha de compra de un paquete (solo PATCH).
    Responde con el estado completo para que el frontend muestre el nuevo
    vencimiento."""

    queryset = Package.objects.select_related("student", "package_type")
    permission_classes = [IsReceptionistOrAdmin]
    serializer_class = PackagePurchaseDateSerializer
    http_method_names = ["patch", "options"]

    def update(self, request, *args, **kwargs):
        # Aunque llegue por PATCH, purchase_date es obligatorio.
        kwargs["partial"] = False
        super().update(request, *args, **kwargs)
        return Response(PackageStatusSerializer(self.get_object()).data)
