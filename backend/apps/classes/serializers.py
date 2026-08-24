from rest_framework import serializers

from apps.classes.models import ClassOffering


class ClassOfferingSerializer(serializers.ModelSerializer):
    weekday_label = serializers.CharField(source="get_weekday_display", read_only=True)

    class Meta:
        model = ClassOffering
        fields = [
            "id",
            "name",
            "weekday",
            "weekday_label",
            "start_time",
            "end_time",
            "room",
            "instructor_name",
            "is_active",
        ]
