from django.db import models
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.contrib.auth.models import User

class Court(models.Model):
    COURT_TYPE_CHOICES = [
        ('Single', 'Sân Đơn'),
        ('Double', 'Sân Đôi'),
    ]

    CourtName = models.CharField(max_length=100)
    Location = models.CharField(max_length=100)
    OpeningHours = models.TimeField()
    ClosingHours = models.TimeField()
    Active = models.BooleanField(default=True)
    CourtType = models.CharField(max_length=10, choices=COURT_TYPE_CHOICES)
    WeekdayPrice = models.DecimalField(max_digits=10, decimal_places=3)
    WeekendPrice = models.DecimalField(max_digits=10, decimal_places=3)

    def __str__(self):
        return f"{self.CourtName} - {self.Location} ({self.CourtType})"

    def update_active_status(self):
        now = datetime.now().time()
        self.Active = self.ClosingHours > now
        self.save()


class Schedule(models.Model):
    SCHEDULE_TYPE_CHOICES = [
        ('Fixed', 'Lịch cố định'),
        ('Daily', 'Đặt lịch ngày'),
        ('Flexible', 'Lịch linh hoạt'),
    ]

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="schedules",
        null=True,
        blank=True
    )
    court = models.ForeignKey('Court', on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_TYPE_CHOICES)
    days = models.JSONField(null=True, blank=True)
    duration = models.PositiveIntegerField(null=True, blank=True)
    total_hours = models.PositiveIntegerField(null=True, blank=True)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.schedule_type} ({self.date}) - {self.court.CourtName}"

    def calculate_price(self):
        if self.schedule_type == 'Fixed':
            return self.court.WeekdayPrice * len(self.days) * 4 * self.duration
        elif self.schedule_type == 'Daily':
            return self.court.WeekdayPrice
        elif self.schedule_type == 'Flexible':
            return self.court.WeekdayPrice * self.total_hours

    def clean(self):
        # Kiểm tra logic lịch "Daily" và "Fixed"
        if self.schedule_type in ['Daily', 'Fixed']:
            if self.schedule_type == 'Daily' and not self.date:
                raise ValidationError("Date is required for Daily schedules.")
            if self.schedule_type == 'Fixed':
                if not self.days:
                    raise ValidationError("Fixed schedule requires selected days.")
                if not self.start_time or not self.end_time:
                    raise ValidationError("Fixed schedule requires both start time and end time.")
                if self.start_time >= self.end_time:
                    raise ValidationError("Start time must be earlier than end time.")

            # Kiểm tra xung đột lịch
            if self.start_time and self.end_time:
                conflicting_schedule = Schedule.objects.filter(
                    court=self.court,
                    start_time__lt=self.end_time,
                    end_time__gt=self.start_time,
                ).exclude(id=self.id)

                if self.schedule_type == 'Fixed'and self.days:
                    conflicting_schedule = conflicting_schedule.filter(days__overlap=self.days)
                elif self.schedule_type == 'Daily' and self.date:
                    conflicting_schedule = conflicting_schedule.filter(date=self.date)

                if conflicting_schedule.exists():
                    raise ValidationError("Schedule conflicts with an existing booking.")

        # Kiểm tra logic lịch "Flexible"
        if self.schedule_type == 'Flexible':
            if not self.total_hours:
                raise ValidationError("Total hours are required for Flexible schedules.")
            if self.total_hours <= 0:
                raise ValidationError("Total hours must be greater than zero.")
            if self.total_hours > 100:
                raise ValidationError("Total hours must be less than or equal to 100.")

            # Tính tổng số giờ đã đăng ký trong tháng
            if self.schedule_type == 'Flexible' and self.date:
                total_registered_hours = Schedule.objects.filter(
                    customer=self.customer,
                    schedule_type='Flexible',
                    date__year=self.date.year,
                    date__month=self.date.month,
                ).aggregate(Sum('total_hours'))['total_hours__sum'] or 0

                if total_registered_hours + self.total_hours > 100:
                    raise ValidationError(
                        f"Flexible schedule exceeds monthly limit. Already registered: {total_registered_hours} hours."
                    )

    def save(self, *args, **kwargs):
        # Đảm bảo khách hàng được gán trước khi lưu
        if not self.customer and not kwargs.get('bypass_customer_check', False):
            raise ValueError("Customer must be assigned before saving.")
        self.clean()

        is_new = self.pk is None  # Kiểm tra xem đối tượng có phải là đối tượng mới hay không
        super().save(*args, **kwargs)

        # Tính toán ngày hết hạn cho lịch cố định
        if self.schedule_type == "Fixed" and self.duration and is_new:
            self.expired_at = self.created_at + timedelta(weeks=self.duration * 4)
            super().save(update_fields=['expired_at'])  # Lưu chỉ trường expired_at
