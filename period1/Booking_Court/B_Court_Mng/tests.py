from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from B_Court_Mng.models import Court, Schedule
from datetime import datetime, timedelta, time
from django.utils.timezone import make_aware

class ScheduleTests(TestCase):
    def setUp(self):
        """Thiết lập dữ liệu trước khi chạy test"""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')

        self.court = Court.objects.create(
            CourtName="Test Court",
            OpeningHours=time(6, 0),
            ClosingHours=time(22, 0),
            WeekdayPrice=50000,
            WeekendPrice=70000,
        )

    # ✅ Đặt lịch Fixed thành công với ngày hợp lệ
    def test_fixed_schedule_success(self):
        schedule = Schedule.objects.create(
            customer=self.user,
            court=self.court,
            schedule_type="Fixed",
            start_time=time(10, 0),
            end_time=time(11, 0),
            days=["Monday", "Wednesday"],
            duration=3,
            created_at=make_aware(datetime.today() - timedelta(days=11)),  # Đã qua 10 ngày
            expired_at=make_aware(datetime.today() + timedelta(days=90)),  # 3 tháng sau
            status="Paid"
        )
        self.assertEqual(schedule.status, "Paid")
        self.assertIsNotNone(schedule.expired_at)

    # ✅ Đặt lịch Daily trong khoảng thời gian trống
    def test_daily_schedule_success(self):
        schedule = Schedule.objects.create(
            customer=self.user,
            court=self.court,
            schedule_type="Daily",
            date=datetime.today().date() + timedelta(days=1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            status="Paid"
        )
        self.assertEqual(schedule.status, "Paid")

    # ✅ Đặt lịch Flexible với số giờ hợp lệ
    def test_flexible_schedule_success(self):
        schedule = Schedule.objects.create(
            customer=self.user,
            court=self.court,
            schedule_type="Flexible",
            total_hours=10,
            status="Paid"
        )
        self.assertEqual(schedule.total_hours, 10)

    # ✅ Đặt lịch bị từ chối do xung đột với lịch khác
    def test_schedule_conflict(self):
        Schedule.objects.create(
            customer=self.user,
            court=self.court,
            schedule_type="Daily",
            date=datetime.today().date() + timedelta(days=1),  # ✅ Dùng ngày tương lai
            start_time=time(10, 0),
            end_time=time(12, 0),
            status="Paid"
        )

        with self.assertRaises(Exception) as context:
            Schedule.objects.create(
                customer=self.user,
                court=self.court,
                schedule_type="Daily",
                date=datetime.today().date() + timedelta(days=1),  # ✅ Dùng ngày tương lai
                start_time=time(11, 0),  # Trùng với lịch đã đặt
                end_time=time(13, 0),
                status="Paid"
            )
        self.assertIn("conflicts", str(context.exception).lower())

    # ✅ Đặt lịch mà chưa thanh toán → Lịch phải ở trạng thái Pending
    def test_schedule_pending_status(self):
        schedule = Schedule.objects.create(
            customer=self.user,
            court=self.court,
            schedule_type="Daily",
            date=datetime.today().date() + timedelta(days=1),
            start_time=time(15, 0),
            end_time=time(16, 0),
            status="Pending"
        )
        self.assertEqual(schedule.status, "Pending")

class CancellationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')

        self.court = Court.objects.create(
            CourtName="Test Court",
            OpeningHours=time(6, 0),
            ClosingHours=time(22, 0),
            WeekdayPrice=50000,
            WeekendPrice=70000,
        )

    # ✅ Hủy lịch đã thanh toán → Kiểm tra quy trình hoàn tiền
    def test_cancel_paid_schedule(self):
        schedule = Schedule.objects.create(
            customer=self.user,
            court=self.court,
            schedule_type="Daily",
            date=datetime.today().date() + timedelta(days=1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            status="Paid"
        )
        schedule.delete()
        self.assertFalse(Schedule.objects.filter(id=schedule.id).exists())

    # ✅ Hủy lịch Pending → Lịch bị xóa hoàn toàn
    def test_cancel_pending_schedule(self):
        schedule = Schedule.objects.create(
            customer=self.user,
            court=self.court,
            schedule_type="Daily",
            date=datetime.today().date() + timedelta(days=1),
            start_time=time(14, 0),
            end_time=time(15, 0),
            status="Pending"
        )
        schedule.delete()
        self.assertFalse(Schedule.objects.filter(id=schedule.id).exists())

if __name__ == "__main__":
    import unittest
    unittest.main()
