from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.accounts.models import Student

PHONE_TAKEN_MESSAGE = "Ya existe un alumno con este teléfono."


def unique_phone_field():
    return serializers.CharField(
        max_length=20,
        validators=[UniqueValidator(Student.objects.all(), message=PHONE_TAKEN_MESSAGE)],
    )


class StudentLoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    pin = serializers.CharField()


class StudentPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["id", "first_name", "last_name", "phone", "email", "category"]


class StudentStaffSerializer(serializers.ModelSerializer):
    """Recepción/administración: listar y corregir datos de un alumno.

    `pin` es opcional y de solo escritura: si llega con valor se asigna
    como PIN nuevo; vacío o ausente deja el PIN actual. El PIN (ni su
    hash) nunca se devuelve."""

    phone = unique_phone_field()
    pin = serializers.CharField(
        write_only=True, required=False, allow_blank=True, max_length=8
    )

    class Meta:
        model = Student
        fields = [
            "id",
            "first_name",
            "last_name",
            "phone",
            "email",
            "document_id",
            "category",
            "pin",
        ]

    def validate_pin(self, value):
        if value and len(value) < 4:
            raise serializers.ValidationError("El PIN debe tener entre 4 y 8 caracteres.")
        return value

    def update(self, instance, validated_data):
        pin = validated_data.pop("pin", "")
        if pin:
            instance.set_pin(pin)
        return super().update(instance, validated_data)


class StudentRegisterSerializer(serializers.ModelSerializer):
    """Used by recepción to register a new student (sets the initial PIN)."""

    phone = unique_phone_field()
    pin = serializers.CharField(write_only=True, min_length=4, max_length=8)

    class Meta:
        model = Student
        fields = [
            "id",
            "first_name",
            "last_name",
            "phone",
            "email",
            "document_id",
            "category",
            "pin",
        ]

    def create(self, validated_data):
        pin = validated_data.pop("pin")
        request = self.context.get("request")
        student = Student(**validated_data)
        student.set_pin(pin)
        if request and request.user and request.user.is_authenticated:
            student.registered_by = request.user
        student.save()
        return student
