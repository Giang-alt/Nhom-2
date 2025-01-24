from django.db import models
from datetime import datetime
from django.contrib.auth.models import AbstractUser

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
        if self.ClosingHours <= now:  
            self.Active = False
        else:
            self.Active = True
        self.save()  

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    
    def __str__(self):
        return f"{self.name} - {self.email} ({self.phone})"
# Người dùng (user)
class User(AbstractUser):
    # Các trường khác của bạn ở đây
    groups = models.ManyToManyField(
        'auth.Group', related_name='b_court_mng_user_set', blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', related_name='b_court_mng_user_permissions_set', blank=True
    )
# Lịch đăng ký (booking)
class Booking(models.Model):
    BOOKING_TYPE_CHOICES = [
        ('fixed', 'Fixed Schedule'),
        ('daily', 'Daily Schedule'),
        ('flexible', 'Flexible Schedule'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    court = models.ForeignKey('Court', on_delete=models.CASCADE)
    booking_type = models.CharField(max_length=10, choices=BOOKING_TYPE_CHOICES)
    booking_date = models.DateField(null=True, blank=True)
    time_slot = models.TimeField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)  # Giờ bắt đầu
    end_time = models.TimeField(null=True, blank=True)  # Giờ kết thúc
    date = models.DateField(null=True, blank=True)
    fixed_day = models.CharField(max_length=10, null=True, blank=True)  # Thứ trong tuần
    fixed_months = models.IntegerField(null=True, blank=True)  # Số tháng
    flexible_hours = models.IntegerField(null=True, blank=True)  # Tổng số giờ
    check_in_status = models.BooleanField(default=False)  # Trạng thái Check-In
    def __str__(self):
        return f"{self.user} - {self.court} - {self.booking_type}"
#class CheckIn(models.Model):
 #   booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
  #  check_in_time = models.DateTimeField(auto_now_add=True)

  #  def __str__(self):
    #    return f"Check-in for booking {self.booking.id} at {self.check_in_time}"