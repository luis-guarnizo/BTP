from rest_framework import serializers

from apps.accounts.models import Student


class StudentLoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    pin = serializers.CharField()


class StudentPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["id", "first_name", "last_name", "phone", "email", "category"]


class StudentRegisterSerializer(serializers.ModelSerializer):
    """Used by recepción to register a new student (sets the initial PIN)."""

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
