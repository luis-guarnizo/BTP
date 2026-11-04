from django.contrib.auth.models import Group, User
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import Student


def make_student(phone, pin="1234", **extra):
    data = {"first_name": "Ana", "last_name": "Perez", "category": Student.CATEGORY_SOCIAL}
    data.update(extra)
    student = Student(phone=phone, **data)
    student.set_pin(pin)
    student.save()
    return student


class StudentEditTests(TestCase):
    def setUp(self):
        group, _ = Group.objects.get_or_create(name="Recepcionista")
        self.receptionist = User.objects.create_user("recepcion", password="x")
        self.receptionist.groups.add(group)
        self.admin = User.objects.create_superuser("admin", password="x")
        self.client = APIClient()
        self.client.force_authenticate(self.receptionist)
        self.student = make_student("3001112233", email="ana@example.com")

    def url(self, student=None):
        return f"/api/accounts/students/{(student or self.student).pk}/"

    def checkin_login(self, phone, pin):
        return APIClient().post(
            "/api/accounts/checkin-login/", {"phone": phone, "pin": pin}, format="json"
        )

    def test_receptionist_edits_all_fields(self):
        response = self.client.patch(
            self.url(),
            {
                "first_name": "Anna",
                "last_name": "Pérez",
                "phone": "3009998877",
                "email": "anna@example.com",
                "document_id": "1020304050",
                "category": Student.CATEGORY_LINEAS,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.student.refresh_from_db()
        self.assertEqual(self.student.first_name, "Anna")
        self.assertEqual(self.student.last_name, "Pérez")
        self.assertEqual(self.student.phone, "3009998877")
        self.assertEqual(self.student.email, "anna@example.com")
        self.assertEqual(self.student.document_id, "1020304050")
        self.assertEqual(self.student.category, Student.CATEGORY_LINEAS)

    def test_admin_can_edit(self):
        client = APIClient()
        client.force_authenticate(self.admin)
        response = client.patch(self.url(), {"first_name": "Anita"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.student.refresh_from_db()
        self.assertEqual(self.student.first_name, "Anita")

    def test_anonymous_cannot_edit(self):
        response = APIClient().patch(self.url(), {"first_name": "X"}, format="json")
        self.assertEqual(response.status_code, 403)
        self.student.refresh_from_db()
        self.assertEqual(self.student.first_name, "Ana")

    def test_duplicate_phone_is_rejected_in_spanish(self):
        other = make_student("3005556677")
        response = self.client.patch(self.url(other), {"phone": "3001112233"}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["phone"], ["Ya existe un alumno con este teléfono."])
        other.refresh_from_db()
        self.assertEqual(other.phone, "3005556677")

    def test_keeping_own_phone_is_allowed(self):
        response = self.client.patch(
            self.url(), {"phone": "3001112233", "first_name": "Ana María"}, format="json"
        )
        self.assertEqual(response.status_code, 200)

    def test_register_duplicate_phone_uses_same_message(self):
        response = self.client.post(
            "/api/accounts/students/",
            {
                "first_name": "Luis",
                "last_name": "Gil",
                "phone": "3001112233",
                "category": Student.CATEGORY_SOCIAL,
                "pin": "1111",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["phone"], ["Ya existe un alumno con este teléfono."])

    def test_required_fields_cannot_be_blank(self):
        for field in ("first_name", "last_name", "phone"):
            with self.subTest(field=field):
                response = self.client.patch(self.url(), {field: ""}, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)
        self.student.refresh_from_db()
        self.assertEqual(
            (self.student.first_name, self.student.last_name, self.student.phone),
            ("Ana", "Perez", "3001112233"),
        )

    def test_invalid_email_is_rejected(self):
        response = self.client.patch(self.url(), {"email": "no-es-correo"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_new_pin_replaces_old_one(self):
        response = self.client.patch(self.url(), {"pin": "5678"}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.checkin_login("3001112233", "5678").status_code, 200)
        self.assertEqual(self.checkin_login("3001112233", "1234").status_code, 401)

    def test_blank_pin_keeps_current_one(self):
        response = self.client.patch(
            self.url(), {"first_name": "Anna", "pin": ""}, format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.checkin_login("3001112233", "1234").status_code, 200)

    def test_short_pin_is_rejected(self):
        response = self.client.patch(self.url(), {"pin": "123"}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["pin"], ["El PIN debe tener entre 4 y 8 caracteres."])
        self.assertEqual(self.checkin_login("3001112233", "1234").status_code, 200)

    def test_pin_is_never_returned(self):
        responses = [
            self.client.get("/api/accounts/students/").data[0],
            self.client.get(self.url()).data,
            self.client.patch(self.url(), {"pin": "5678"}, format="json").data,
        ]
        for data in responses:
            self.assertNotIn("pin", data)
            self.assertNotIn("pin_hash", data)
            self.assertIn("document_id", data)

    def test_checkin_uses_new_phone(self):
        self.client.patch(self.url(), {"phone": "3009998877"}, format="json")

        self.assertEqual(self.checkin_login("3009998877", "1234").status_code, 200)
        old = self.checkin_login("3001112233", "1234")
        self.assertEqual(old.status_code, 401)
        self.assertEqual(old.data["detail"], "Teléfono o PIN incorrectos.")

    def test_put_is_not_allowed(self):
        response = self.client.put(self.url(), {"first_name": "X"}, format="json")
        self.assertEqual(response.status_code, 405)

    def test_checkin_me_does_not_expose_document_id(self):
        Student.objects.filter(pk=self.student.pk).update(document_id="999")
        student_client = APIClient()
        student_client.post(
            "/api/accounts/checkin-login/",
            {"phone": "3001112233", "pin": "1234"},
            format="json",
        )
        data = student_client.get("/api/accounts/me/").data

        self.assertTrue(data["authenticated"])
        self.assertNotIn("document_id", data["student"])
