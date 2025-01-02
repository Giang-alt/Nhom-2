from django.db import models

# Create your models here.
class Court(models.Model):
    CourtName = models.CharField(max_length=100)
    Location = models.CharField(max_length=100)
    OpeningHours = models.TimeField()
    ClosingHours = models.TimeField()
    Active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.CourtName} {self.Location}"
    