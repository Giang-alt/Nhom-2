from django.contrib import admin
from .models import Courts
# Register your models here.
# admin.site.register(Courts)

class CourtsAdmin(admin.ModelAdmin):
  list_display = ("CourtName", "Location", "OpeningHours", "ClosingHours")
  
admin.site.register(Courts, CourtsAdmin)