from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.accounts.models import Student


class PackageType(models.Model):
    """
    Catálogo de planes. Definidos hoy:

    Social (por créditos, vencen 1 mes después del pago):
      - 1 clase   $25.000
      - 4 clases  $80.000
      - 6 clases  $120.000
      - 8 clases  $200.000

    Líneas (mensualidad ilimitada, vence el día 5 del mes siguiente):
      - Kids        $120.000
      - Amateur     $120.000
      - Semipro     $110.000
      - Profesional $95.000
    """

    CATEGORY_CHOICES = Student.CATEGORY_CHOICES

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    # Number of classes included. Null/blank = unlimited (líneas).
    credit_count = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de paquete"
        verbose_name_plural = "Tipos de paquete"
        ordering = ["category", "price"]

    def __str__(self):
        credits = f"{self.credit_count} clases" if self.credit_count else "ilimitado"
        return f"{self.name} ({self.get_category_display()}, {credits}) - ${self.price:,.0f}"

    @property
    def is_unlimited(self):
        return self.credit_count is None


class Package(models.Model):
    """A specific purchase/renewal made by a student."""

    PAYMENT_CASH = "efectivo"
    PAYMENT_TRANSFER = "transferencia"
    PAYMENT_CHOICES = [
        (PAYMENT_CASH, "Efectivo"),
        (PAYMENT_TRANSFER, "Transferencia"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="packages")
    package_type = models.ForeignKey(PackageType, on_delete=models.PROTECT)
    purchase_date = models.DateField(default=timezone.localdate)
    expires_at = models.DateField(editable=False)
    credits_remaining = models.PositiveIntegerField(null=True, blank=True)
    payment_method = models.CharField(max_length=15, choices=PAYMENT_CHOICES)
    sold_by = models.ForeignKey(
        "auth.User", null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Paquete / mensualidad"
        verbose_name_plural = "Paquetes / mensualidades"
        ordering = ["-purchase_date"]

    def __str__(self):
        return f"{self.student} - {self.package_type} ({self.purchase_date})"

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        # Recordamos la fecha de compra cargada para saber en save() si
        # cambió (p. ej. recepción o el admin la corrigieron) y hay que
        # recalcular el vencimiento.
        instance._loaded_purchase_date = instance.__dict__.get("purchase_date")
        return instance

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        purchase_date_changed = (
            not is_new
            and self.purchase_date != getattr(self, "_loaded_purchase_date", self.purchase_date)
        )
        if is_new or purchase_date_changed:
            self.expires_at = self._compute_expiry()
            update_fields = kwargs.get("update_fields")
            if update_fields is not None and "purchase_date" in update_fields:
                kwargs["update_fields"] = {*update_fields, "expires_at"}
        if is_new and not self.package_type.is_unlimited and self.credits_remaining is None:
            self.credits_remaining = self.package_type.credit_count
        super().save(*args, **kwargs)
        self._loaded_purchase_date = self.purchase_date

    def _compute_expiry(self):
        if self.package_type.category == Student.CATEGORY_LINEAS:
            # Vence el día LINEAS_EXPIRY_DAY del mes siguiente a la compra,
            # sin importar el día de pago (todos comparten el mismo ciclo).
            year, month = self.purchase_date.year, self.purchase_date.month + 1
            if month > 12:
                year, month = year + 1, 1
            return self.purchase_date.replace(
                year=year, month=month, day=settings.LINEAS_EXPIRY_DAY
            )
        # Social: 1 mes después del pago; si no usa las clases, las pierde.
        return self.purchase_date + timedelta(days=settings.SOCIAL_PACKAGE_VALIDITY_DAYS)

    @property
    def is_expired(self) -> bool:
        return timezone.localdate() > self.expires_at

    @property
    def is_exhausted(self) -> bool:
        return self.credits_remaining is not None and self.credits_remaining <= 0

    @property
    def status(self) -> str:
        if self.is_exhausted:
            return "agotado"
        if self.is_expired:
            return "vencido"
        return "activo"

    @property
    def is_usable(self) -> bool:
        return self.status == "activo"

    def consume_credit(self):
        """Only applies to social (credit-based) packages."""
        if self.credits_remaining is not None:
            self.credits_remaining = max(self.credits_remaining - 1, 0)
            self.save(update_fields=["credits_remaining"])
