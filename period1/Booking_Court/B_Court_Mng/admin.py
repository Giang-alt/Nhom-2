from django.contrib import admin
from .models import Court
# Register your models here.
# admin.site.register(Courts)

class CourtsAdmin(admin.ModelAdmin):
  list_display = ("CourtName", "Location", "OpeningHours", "ClosingHours",'CourtType', 'WeekdayPrice', 'WeekendPrice', "Active")
  
admin.site.register(Court, CourtsAdmin)