from django import forms
from django.contrib import admin

from apps.accounts.models import Student


class StudentAdminForm(forms.ModelForm):
    pin = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        help_text="Déjalo vacío para no cambiar el PIN actual.",
    )

    class Meta:
        model = Student
        fields = [
            "first_name",
            "last_name",
            "phone",
            "email",
            "document_id",
            "category",
            "is_active",
            "pin",
        ]

    def save(self, commit=True):
        student = super().save(commit=False)
        pin = self.cleaned_data.get("pin")
        if pin:
            student.set_pin(pin)
        elif not student.pin_hash:
            student.set_pin("0000")
        if commit:
            student.save()
        return student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    form = StudentAdminForm
    list_display = ["first_name", "last_name", "phone", "category", "is_active", "created_at"]
    list_filter = ["category", "is_active"]
    search_fields = ["first_name", "last_name", "phone", "document_id", "email"]
