from django.db import models
from datetime import datetime

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

