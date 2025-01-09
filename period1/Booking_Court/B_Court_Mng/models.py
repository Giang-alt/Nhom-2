from django.db import models

# Create your models here.
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
    Price = models.DecimalField(max_digits=6, decimal_places=3)  

    def __str__(self):
        return f"{self.CourtName} - {self.Location} ({self.CourtType})"