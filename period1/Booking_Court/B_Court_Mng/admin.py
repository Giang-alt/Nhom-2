from django.contrib import admin
from django import forms
from .models import Court, Schedule
from datetime import timedelta, datetime, date
from django.contrib import messages

# Quản lý Court
class CourtsAdmin(admin.ModelAdmin):
    list_display = ("CourtName", "Location", "OpeningHours", "ClosingHours", "CourtType", "WeekdayPrice", "WeekendPrice", "Active")
    search_fields = ("CourtName", "Location")
    list_filter = ("CourtType", "Active")

admin.site.register(Court, CourtsAdmin)

# Quản lý Schedule
class ScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "customer", 
        "court", 
        "schedule_type",
        "date",
        "days_display",
        "start_time", 
        "end_time",
        "duration",
        "total_hours",  # Hiển thị số giờ (nếu là Flexible)
        "status",
        "checked_in",
        "created_at",   
        "expired_at_display",   # Hiển thị thời gian hết hạn lịch (nếu có)
    )
    list_filter = ("schedule_type", "status", "checked_in", "created_at")
    search_fields = ("customer__username", "court__CourtName", "created_at")
    # Chỉ đọc một số trường nếu lịch đã thanh toán
    readonly_fields = ("customer", "court", "schedule_type", "created_at", "expired_at", "days", "date", "duration")

    def days_display(self, obj):
        """Hiển thị danh sách ngày nếu có"""
        return ", ".join(obj.days) if obj.days else "-"
    days_display.short_description = "Days"
    
    def expired_at_display(self, obj):
        """Hiển thị ngày hết hạn của lịch Fixed."""
        if obj.schedule_type == "Fixed" and obj.duration:
            # Tính ngày hết hạn từ ngày bắt đầu hoạt động (sau 10 ngày)
            activation_date = obj.created_at.date() + timedelta(days=10)
            expiration_date = activation_date + timedelta(weeks=obj.duration * 4)
            return expiration_date if expiration_date >= datetime.today().date() else "Expired"
        return "N/A"
    expired_at_display.short_description = "Expired At"
    
    # def get_readonly_fields(self, request, obj=None):
    #     """Không cho chỉnh sửa start_time & end_time nếu lịch đã xác nhận."""
    #     if obj and obj.is_confirmed:
    #         return self.readonly_fields + ("start_time", "end_time", "total_hours")
    #     return self.readonly_fields

    # def has_delete_permission(self, request, obj=None):
    #     """Chặn xóa lịch đã hết hạn hoặc đã xác nhận."""
    #     if obj and (obj.status == 'confirmed' or (obj.expired_at and obj.expired_at.date() < datetime.today().date())):
    #         return False
    #     return super().has_delete_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        """Cho phép chỉnh sửa nếu đã check-in hoặc nếu là Flexible"""
        if obj and obj.schedule_type == "Lịch linh hoạt" and obj.checked_in:
            return True
        return super().has_change_permission(request, obj)

    @admin.action(description="Xóa lịch đã hết hạn")
    def delete_expired_schedules(self, request, queryset):
        """Hành động xóa lịch đã hết hạn."""
        expired_schedules = []
        for schedule in queryset:
            if schedule.schedule_type == "Fixed" and schedule.duration:
                activation_date = schedule.created_at.date() + timedelta(days=10)
                expiration_date = activation_date + timedelta(weeks=schedule.duration * 4)
                if expiration_date < datetime.today().date():
                    expired_schedules.append(schedule)
        
        count = len(expired_schedules)
        for schedule in expired_schedules:
            schedule.delete()

        self.message_user(request, f"{count} lịch hết hạn đã được xóa.")

    delete_expired_schedules.short_description = "Xóa lịch đã hết hạn"

    actions = [delete_expired_schedules]

    @admin.action(description="Gia hạn lịch Fixed thêm 1 tháng")
    def extend_fixed_schedule(self, request, queryset):
        """Gia hạn lịch cố định thêm 1 tháng."""
        count = 0
        for schedule in queryset:
            if schedule.schedule_type == "Fixed" and schedule.expired_at:
                schedule.expired_at += timedelta(weeks=4)
                schedule.save()
                count += 1
        self.message_user(request, f"{count} lịch cố định đã được gia hạn thêm 1 tháng.")

    actions = [delete_expired_schedules, extend_fixed_schedule]

    @admin.action(description="Đánh dấu lịch đã check-in")
    def mark_checked_in(self, request, queryset):
        """Cho phép staff đánh dấu lịch đã check-in"""
        schedules_to_check_in = queryset.filter(checked_in=False)
        count = schedules_to_check_in.update(checked_in=True)
        self.message_user(request, f"{count} lịch đã được đánh dấu là Check-in.")

    actions = [delete_expired_schedules, mark_checked_in, extend_fixed_schedule]

admin.site.register(Schedule, ScheduleAdmin)
