from rest_framework import serializers

from apps.attendance.models import CheckIn


class CheckInRequestSerializer(serializers.Serializer):
    class_offering_id = serializers.IntegerField()


class CheckInResultSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source="class_offering.name")
    credits_remaining = serializers.SerializerMethodField()

    class Meta:
        model = CheckIn
        fields = [
            "id",
            "class_name",
            "checked_in_at",
            "credit_deducted",
            "credits_remaining",
        ]

    def get_credits_remaining(self, obj):
        return obj.package.credits_remaining if obj.package else None
