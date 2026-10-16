from datetime import date, timedelta
from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import Student
from apps.packages.models import Package, PackageType


def make_student(category, phone):
    student = Student(first_name="Ana", last_name="Pérez", phone=phone, category=category)
    student.set_pin("1234")
    student.save()
    return student


class PackageFixturesMixin:
    @classmethod
    def setUpTestData(cls):
        cls.social_type = PackageType.objects.create(
            name="4 clases", category=Student.CATEGORY_SOCIAL, price=80000, credit_count=4
        )
        cls.lineas_type = PackageType.objects.create(
            name="Amateur", category=Student.CATEGORY_LINEAS, price=120000
        )
        cls.social_student = make_student(Student.CATEGORY_SOCIAL, "3000000001")
        cls.lineas_student = make_student(Student.CATEGORY_LINEAS, "3000000002")

    def sell(self, package_type, purchase_date, student=None):
        if student is None:
            student = (
                self.lineas_student
                if package_type.category == Student.CATEGORY_LINEAS
                else self.social_student
            )
        return Package.objects.create(
            student=student,
            package_type=package_type,
            purchase_date=purchase_date,
            payment_method=Package.PAYMENT_CASH,
        )


class ExpiryRuleTests(PackageFixturesMixin, TestCase):
    def test_lineas_expires_on_day_5_of_next_month(self):
        for purchase in (date(2026, 9, 3), date(2026, 9, 5), date(2026, 9, 20)):
            with self.subTest(purchase=purchase):
                pkg = self.sell(self.lineas_type, purchase)
                self.assertEqual(pkg.expires_at, date(2026, 10, 5))

    def test_lineas_december_rolls_over_to_january(self):
        pkg = self.sell(self.lineas_type, date(2026, 12, 15))
        self.assertEqual(pkg.expires_at, date(2027, 1, 5))

    def test_social_expires_30_days_after_purchase(self):
        pkg = self.sell(self.social_type, date(2026, 10, 15))
        self.assertEqual(pkg.expires_at, date(2026, 11, 14))
        self.assertEqual(pkg.credits_remaining, 4)


class PurchaseDateEditTests(PackageFixturesMixin, TestCase):
    def test_editing_purchase_date_recalculates_expiry(self):
        pkg = self.sell(self.social_type, date(2026, 10, 10))
        self.assertEqual(pkg.expires_at, date(2026, 11, 9))

        pkg = Package.objects.get(pk=pkg.pk)
        pkg.purchase_date = date(2026, 10, 8)
        pkg.save()

        pkg.refresh_from_db()
        self.assertEqual(pkg.expires_at, date(2026, 11, 7))

    def test_update_fields_with_purchase_date_also_saves_expiry(self):
        pkg = self.sell(self.lineas_type, date(2026, 9, 5))
        pkg = Package.objects.get(pk=pkg.pk)
        pkg.purchase_date = date(2026, 10, 2)
        pkg.save(update_fields=["purchase_date"])

        pkg.refresh_from_db()
        self.assertEqual(pkg.expires_at, date(2026, 11, 5))

    def test_editing_purchase_date_keeps_credits(self):
        pkg = self.sell(self.social_type, date(2026, 10, 10))
        pkg.credits_remaining = 3
        pkg.save(update_fields=["credits_remaining"])

        pkg = Package.objects.get(pk=pkg.pk)
        pkg.purchase_date = date(2026, 10, 1)
        pkg.save()

        pkg.refresh_from_db()
        self.assertEqual(pkg.credits_remaining, 3)

    def test_consume_credit_does_not_touch_expiry(self):
        pkg = self.sell(self.social_type, date(2026, 10, 10))
        pkg = Package.objects.get(pk=pkg.pk)
        pkg.consume_credit()

        pkg.refresh_from_db()
        self.assertEqual(pkg.credits_remaining, 3)
        self.assertEqual(pkg.expires_at, date(2026, 11, 9))

    def test_active_package_tiebreak_uses_latest_registered(self):
        older = self.sell(self.social_type, date(2026, 10, 10))
        newer = self.sell(self.social_type, date(2026, 10, 10))
        Package.objects.filter(pk=older.pk).update(
            created_at=newer.created_at - timedelta(hours=1)
        )
        self.assertEqual(self.social_student.active_package(), newer)


class PackageApiTests(PackageFixturesMixin, TestCase):
    def setUp(self):
        group, _ = Group.objects.get_or_create(name="Recepcionista")
        self.receptionist = User.objects.create_user("recepcion", password="x")
        self.receptionist.groups.add(group)
        self.client = APIClient()
        self.client.force_authenticate(self.receptionist)

    def url(self, pkg):
        return f"/api/packages/{pkg.pk}/"

    def test_receptionist_edits_purchase_date(self):
        today = timezone.localdate()
        pkg = self.sell(self.social_type, today - timedelta(days=40))
        self.assertEqual(pkg.status, "vencido")

        response = self.client.patch(
            self.url(pkg), {"purchase_date": today.isoformat()}, format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["purchase_date"], today.isoformat())
        self.assertEqual(response.data["expires_at"], (today + timedelta(days=30)).isoformat())
        self.assertEqual(response.data["status"], "activo")

    def test_only_purchase_date_is_editable(self):
        pkg = self.sell(self.social_type, date(2026, 10, 10))
        response = self.client.patch(
            self.url(pkg),
            {
                "purchase_date": "2026-10-08",
                "credits_remaining": 99,
                "package_type": self.lineas_type.pk,
                "payment_method": Package.PAYMENT_TRANSFER,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        pkg.refresh_from_db()
        self.assertEqual(pkg.purchase_date, date(2026, 10, 8))
        self.assertEqual(pkg.credits_remaining, 4)
        self.assertEqual(pkg.package_type, self.social_type)
        self.assertEqual(pkg.payment_method, Package.PAYMENT_CASH)

    def test_invalid_or_missing_date_is_rejected(self):
        pkg = self.sell(self.social_type, date(2026, 10, 10))
        for body in ({"purchase_date": ""}, {"purchase_date": "10/08/2026"}, {}):
            with self.subTest(body=body):
                response = self.client.patch(self.url(pkg), body, format="json")
                self.assertEqual(response.status_code, 400)
                pkg.refresh_from_db()
                self.assertEqual(pkg.purchase_date, date(2026, 10, 10))

    def test_anonymous_cannot_edit(self):
        pkg = self.sell(self.social_type, date(2026, 10, 10))
        response = APIClient().patch(
            self.url(pkg), {"purchase_date": "2026-10-01"}, format="json"
        )
        self.assertEqual(response.status_code, 403)
        pkg.refresh_from_db()
        self.assertEqual(pkg.purchase_date, date(2026, 10, 10))

    def test_put_is_not_allowed(self):
        pkg = self.sell(self.social_type, date(2026, 10, 10))
        response = self.client.put(self.url(pkg), {"purchase_date": "2026-10-01"}, format="json")
        self.assertEqual(response.status_code, 405)

    def test_create_with_explicit_purchase_date(self):
        yesterday = timezone.localdate() - timedelta(days=1)
        response = self.client.post(
            "/api/packages/",
            {
                "student": self.social_student.pk,
                "package_type": self.social_type.pk,
                "payment_method": Package.PAYMENT_CASH,
                "purchase_date": yesterday.isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        pkg = Package.objects.get(pk=response.data["id"])
        self.assertEqual(pkg.purchase_date, yesterday)
        self.assertEqual(pkg.expires_at, yesterday + timedelta(days=30))
        self.assertEqual(pkg.sold_by, self.receptionist)

    def test_create_without_purchase_date_uses_today(self):
        response = self.client.post(
            "/api/packages/",
            {
                "student": self.social_student.pk,
                "package_type": self.social_type.pk,
                "payment_method": Package.PAYMENT_CASH,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        today = timezone.localdate()
        pkg = Package.objects.get(pk=response.data["id"])
        self.assertEqual(pkg.purchase_date, today)
        self.assertEqual(pkg.expires_at, today + timedelta(days=30))
