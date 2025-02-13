from django.db import models
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from dateutil.relativedelta import relativedelta

class Court(models.Model):
    COURT_TYPE_CHOICES = [
        ('Single', 'Sân Đơn'),
        ('Double', 'Sân Đôi'),
    ]

    CourtName = models.CharField(max_length=100)
    Location = models.CharField(max_length=100)
    OpeningHours = models.TimeField()  # Giờ mở cửa
    ClosingHours = models.TimeField()  # Giờ đóng cửa
    Active = models.BooleanField(default=False)  # Mặc định là không hoạt động
    CourtType = models.CharField(max_length=10, choices=COURT_TYPE_CHOICES)
    WeekdayPrice = models.DecimalField(max_digits=10, decimal_places=3)
    WeekendPrice = models.DecimalField(max_digits=10, decimal_places=3)

    def __str__(self):
        return f"{self.CourtName} - {self.Location} ({self.CourtType})"

    def update_active_status(self):
        now = datetime.now().time()  # Lấy thời gian hiện tại

        # Kiểm tra xem giờ hiện tại có nằm trong giờ mở cửa không
        if self.OpeningHours <= now <= self.ClosingHours:
            self.Active = True  # Hoạt động
        else:
            self.Active = False  # Không hoạt động
        
        self.save()  # Lưu lại trạng thái mới của sân

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    
    def __str__(self):
        return f"{self.name} - {self.email} ({self.phone})"

class Schedule(models.Model):
    SCHEDULE_TYPE_CHOICES = [
        ('Fixed', 'Lịch cố định'),
        ('Daily', 'Đặt lịch ngày'),
        ('Flexible', 'Lịch linh hoạt'),
    ]

    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('pending', 'Pending Payment'),
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
    # is_confirmed = models.BooleanField(default=False)    
    checked_in = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(null=True, blank=True)
    # time_slot = models.CharField(max_length=10, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

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
        now = datetime.now()
        # Kiểm tra lịch Daily
        if self.schedule_type == 'Daily':
            if not self.date:
                raise ValidationError(" Hãy xem thông tin giờ trống và đặt lịch lại.")
            if self.date < datetime.now().date():
                raise ValidationError("Không thể chọn ngày trong quá khứ.")
            if not self.start_time or not self.end_time:
                raise ValidationError("Start and end time are required for Daily schedules.")

            # max_date = now.date() + timedelta(days=9)
            # if self.date > max_date:
            #     self.status = 'pending'  # Đặt trạng thái là "pending"
            #     # Không raise ValidationError, vì lịch sẽ chờ phê duyệt
            # else:
            #     self.status = 'Paid'
            
            closing_time = self.court.ClosingHours
            if self.date == now.date():
                # Nếu đã sau giờ đóng cửa, không cho phép đặt hôm nay
                if now.time() > closing_time:
                    raise ValidationError("Đã quá giờ đóng cửa, vui lòng chọn ngày khác.")
    
                # Kiểm tra nếu giờ đặt trước thời gian hiện tại
                if self.start_time < now.time():
                    raise ValidationError("Không thể đặt sân trước thời gian hiện tại.")

            # Kiểm tra thời gian đặt (ít nhất 1 giờ)
            if self.start_time and self.end_time:
                if self.start_time >= self.end_time:
                    raise ValidationError("Start time must be earlier than end time.")
                if (datetime.combine(self.date, self.end_time) - datetime.combine(self.date, self.start_time)).seconds < 3600:
                    raise ValidationError("Booking duration must be at least 1 hour.")

            # Kiểm tra giờ trống
            conflicting_bookings = Schedule.objects.filter(
                court=self.court,
                date=self.date,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
            ).exclude(pk=self.pk)
            if conflicting_bookings.exists():
                raise ValidationError("Selected time conflicts with an existing booking.")

        # Kiểm tra lịch Fixed
        elif self.schedule_type == 'Fixed':
            if not self.start_time or not self.end_time:
                raise ValidationError("Vui lòng xem lại giờ trống.")
            # if not self.duration or self.duration < 1 or self.duration > 6:
            #     raise ValidationError("Duration must be between 1 and 6 months.")

            # Ràng buộc thời gian đặt (ít nhất 1 giờ)
            if self.start_time >= self.end_time:
                raise ValidationError("Start time must be earlier than end time.")
            if (datetime.combine(now.date(), self.end_time) - datetime.combine(now.date(), self.start_time)).seconds < 3600:
                raise ValidationError("Booking start-end time must be at least 1 hour.")

            # Ràng buộc thời gian duy trì (tối đa 6 tháng, không thấp hơn 1 tháng)
            if self.duration and self.duration < 1 or self.duration > 6:
                raise ValidationError("Fixed schedule duration cannot exceed 6 months.")

        # Kiểm tra lịch Flexible
        # elif self.schedule_type == 'Flexible':
        #     if not self.total_hours or self.total_hours < 1:
        #         raise ValidationError("Total hours must be at least 1.")
        #     if self.total_hours > 100:
        #         raise ValidationError("Total hours cannot exceed 100.")

        super().clean()

    def save(self, *args, **kwargs):
        # Đảm bảo khách hàng được gán trước khi lưu
        if not self.customer and not kwargs.get('bypass_customer_check', False):
            raise ValueError("Customer must be assigned before saving.")
        self.clean()

        is_new = self.pk is None  # Kiểm tra xem đối tượng có phải là đối tượng mới hay không
        super().save(*args, **kwargs)

        # Tính toán ngày hết hạn cho lịch cố định
        if self.schedule_type == "Fixed" and self.duration and is_new:
            activation_date = self.created_at.date() + timedelta(days=10)
            self.expired_at = activation_date + relativedelta(months=self.duration)
            print(f"DEBUG: created_at = {self.created_at}, activation_date = {activation_date}, expired_at = {self.expired_at}")
            super().save(update_fields=['expired_at'])  # Lưu chỉ trường expired_at

    def _day_to_weekday(self, day):
        # Helper: Chuyển thứ (Monday, Tuesday, ...) sang weekday (2: Monday, ..., 7: Sunday, 1: Sunday)
        day_mapping = {
            'Monday': 2,
            'Tuesday': 3,
            'Wednesday': 4,
            'Thursday': 5,
            'Friday': 6,
            'Saturday': 7,
            'Sunday': 1,
        }
        return day_mapping.get(day)
