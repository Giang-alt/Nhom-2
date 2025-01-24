from django.contrib import admin
from .models import Court, Schedule


# Quản lý Court
class CourtsAdmin(admin.ModelAdmin):
    list_display = ("CourtName", "Location", "OpeningHours", "ClosingHours", "CourtType", "WeekdayPrice", "WeekendPrice", "Active")
    search_fields = ("CourtName", "Location")


admin.site.register(Court, CourtsAdmin)


# Quản lý Schedule
class ScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "customer", 
        "court", 
        "schedule_type", 
        "start_time", 
        "end_time", 
        "is_confirmed", 
        "created_at",   # Thời gian đặt lịch
        "expired_at",   # Thời gian hết hạn lịch (nếu có)
    )
    list_filter = ("schedule_type", "is_confirmed", "created_at", "expired_at")
    search_fields = ("customer__username", "court__CourtName", "created_at", "expired_at")

    # Tự động hiển thị expired_at trong admin nếu nó không có trong model
    def expired_at(self, obj):
        if obj.schedule_type == "Fixed" and obj.duration:
            # Tính toán thời gian hết hạn lịch Fixed
            return obj.start_time + timedelta(weeks=obj.duration * 4)
        return None
    expired_at.short_description = "Expired At"


admin.site.register(Schedule, ScheduleAdmin)
