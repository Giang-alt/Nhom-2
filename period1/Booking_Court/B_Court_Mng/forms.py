from django import forms
from B_Court_Mng.models import Court, Schedule
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models import Sum
from datetime import datetime, timedelta, date as datetime_date

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['court', 'schedule_type', 'date', 'days', 'duration', 'total_hours', 'start_time', 'end_time']
        widgets = {
            'days': forms.CheckboxSelectMultiple,
        }

    def clean(self):
        cleaned_data = super().clean()
        schedule_type = cleaned_data.get('schedule_type')
        court = cleaned_data.get('court')

        if not court:
            raise ValidationError("Không tìm thấy sân. Vui lòng thử lại.")

        opening_time = court.OpeningHours
        closing_time = court.ClosingHours

        # Xác định start_time và end_time dựa trên loại lịch
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if schedule_type == 'Fixed':
            days = cleaned_data.get('days', [])

            if not start_time or not end_time or not days:
                self.add_error('start_time', "Vui lòng chọn đầy đủ các trường.")
                return cleaned_data
            # Kiểm tra thời gian đặt lịch nằm trong khoảng mở cửa của sân
            elif start_time < opening_time or end_time > closing_time:
                self.add_error('start_time', f"Thời gian đặt lịch phải nằm trong khoảng {opening_time.strftime('%H:%M')} - {closing_time.strftime('%H:%M')}.")
            # Kiểm tra thời gian đặt lịch tối thiểu là 1 giờ
            elif start_time >= end_time:
                self.add_error('start_time', "Giờ kết thúc phải lớn hơn giờ bắt đầu.")
            elif (datetime.combine(datetime.today(), end_time) - datetime.combine(datetime.today(), start_time)).seconds < 3600:
                self.add_error('start_time', "Thời gian đặt sân tối thiểu là 1 giờ.")    
            # Kiểm tra xung đột lịch cố định
            conflicting_schedule = Schedule.objects.filter(
                court=court,
                days__overlap=days,  
                start_time__lt=end_time,
                end_time__gt=start_time,
            ).exclude(id=self.instance.id)

            if conflicting_schedule.exists():
                self.add_error('start_time', "Lịch cố định bị trùng với một lịch đã có.")

            return cleaned_data
        elif schedule_type == 'Daily':
            date = cleaned_data.get('date')

            if not date:
                self.add_error('date', "Vui lòng chọn một ngày hợp lệ.")
            else:
                if date < datetime_date.today() or date > datetime_date.today() + timedelta(days=9):
                    self.add_error('date', "Bạn chỉ có thể đặt lịch trong vòng 9 ngày từ hôm nay.")

                if date == datetime_date.today():
                    now = datetime.now().time()
                    if now >= closing_time:
                        self.add_error('date', "Không thể đặt lịch cho ngày hôm nay vì đã quá giờ đóng cửa.")

            # Kiểm tra xung đột lịch ngày
            if Schedule.objects.filter(
                court=court,
                schedule_type='Daily',
                date=date,
                start_time__lt=end_time,
                end_time__gt=start_time,
            ).exclude(id=self.instance.id).exists():
                self.add_error('start_time', "Lịch ngày bị trùng với một lịch đã đặt trước đó.")

            # Kiểm tra xung đột với lịch Fixed
            fixed_schedules = Schedule.objects.filter(
                court=court,
                schedule_type='Fixed'
            )

            for fixed_schedule in fixed_schedules:
                # Lấy danh sách Days từ lịch Fixed
                fixed_days = fixed_schedule.days or []

                # Kiểm tra nếu ngày Daily trùng với bất kỳ ngày nào trong Days
                if date.strftime('%A') in fixed_days:
                    # Kiểm tra thời gian trùng lặp
                    if fixed_schedule.start_time < end_time and fixed_schedule.end_time > start_time:
                        self.add_error(
                            'start_time',
                            f"Lịch ngày bị trùng với lịch cố định đã đặt vào ngày {date}."
                        )
                        break

            return cleaned_data
        elif schedule_type == 'Flexible':
            total_hours = cleaned_data.get('total_hours')

            if not total_hours or total_hours <= 0:
                self.add_error('total_hours', "Lịch linh hoạt yêu cầu nhập tổng số giờ hợp lệ.")

            existing_flexible_schedule = Schedule.objects.filter(
                customer=self.instance.customer if hasattr(self.instance, 'customer') else None,
                schedule_type='Flexible',
                created_at__year=datetime_date.today().year,  # Dùng created_at thay vì date
                created_at__month=datetime_date.today().month,
            ).exclude(id=self.instance.id)

            if existing_flexible_schedule.exists():
                self.add_error('total_hours', "Bạn đã có lịch linh hoạt trong tháng này. Không thể đặt thêm lịch mới.")

            total_registered_hours = Schedule.objects.filter(
                customer=self.instance.customer if hasattr(self.instance, 'customer') else None,
                schedule_type='Flexible',
                created_at__year=datetime_date.today().year,
                created_at__month=datetime_date.today().month,
            ).aggregate(Sum('total_hours'))['total_hours__sum'] or 0

            if total_registered_hours + total_hours > 100:
                self.add_error('total_hours', f"Lịch linh hoạt vượt quá giới hạn 100 giờ trong tháng. Đã đăng ký: {total_registered_hours} giờ.")
            
            return cleaned_data

        return cleaned_data

    def save(self, commit=True):
        schedule = super().save(commit=False)

        if hasattr(self, 'request') and self.request.user:
            schedule.customer = self.request.user

        if commit:
            schedule.save()
        return schedule
