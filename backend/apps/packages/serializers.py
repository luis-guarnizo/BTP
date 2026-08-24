from rest_framework import serializers

from apps.packages.models import Package, PackageType


class PackageTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageType
        fields = ["id", "name", "category", "price", "credit_count", "is_active"]


class PackageStatusSerializer(serializers.ModelSerializer):
    """Compact view used by the check-in screen to show the student's
    current package state (créditos restantes / vigencia)."""

    package_type_name = serializers.CharField(source="package_type.name")
    category = serializers.CharField(source="package_type.category")
    status = serializers.CharField()
    is_usable = serializers.BooleanField()
    student = serializers.CharField(source="student.__str__", read_only=True)
    student_id = serializers.IntegerField(source="student.id", read_only=True)

    class Meta:
        model = Package
        fields = [
            "id",
            "student",
            "student_id",
            "package_type_name",
            "category",
            "purchase_date",
            "expires_at",
            "credits_remaining",
            "status",
            "is_usable",
        ]


class PackageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = ["id", "student", "package_type", "purchase_date", "payment_method"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["sold_by"] = request.user
        return super().create(validated_data)
