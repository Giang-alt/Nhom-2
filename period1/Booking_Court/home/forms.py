from django import forms
from B_Court_Mng.models import Court, Schedule
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models import Sum
from B_Court_Mng.models import Booking

class CourtNewForm(forms.ModelForm):
    class Meta:
        model = Court
        fields = ['CourtName', 'Location', 'OpeningHours', 'ClosingHours', 'Active', 'CourtType', 'WeekdayPrice', 'WeekendPrice'] 
        widgets = {
            'OpeningHours': forms.TimeInput(format='%H:%M'),
            'ClosingHours': forms.TimeInput(format='%H:%M'),
        }

class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    
    class Meta:
        model = User
        fields = ['username', 'email']
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        
        if password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data

class ScheduleForm(forms.ModelForm):
    start_time_fixed = forms.TimeField(required=False)
    end_time_fixed = forms.TimeField(required=False)
    start_time_daily = forms.TimeField(required=False)
    end_time_daily = forms.TimeField(required=False)

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
        date = cleaned_data.get('date')
        total_hours = cleaned_data.get('total_hours')
        days = cleaned_data.get('days')

        # Lấy giờ từ các trường nhập
        start_time_fixed = cleaned_data.get('start_time_fixed')
        end_time_fixed = cleaned_data.get('end_time_fixed')
        start_time_daily = cleaned_data.get('start_time_daily')
        end_time_daily = cleaned_data.get('end_time_daily')

        if schedule_type == 'Fixed':
            # Kiểm tra các trường cần thiết cho lịch cố định
            if not days:
                raise ValidationError("Lịch cố định yêu cầu phải chọn ít nhất một ngày.")
            if not start_time_fixed or not end_time_fixed:
                raise ValidationError("Lịch cố định yêu cầu nhập cả giờ bắt đầu và giờ kết thúc.")

            # Ánh xạ giờ cho lịch cố định
            cleaned_data['start_time'] = start_time_fixed
            cleaned_data['end_time'] = end_time_fixed

            # Kiểm tra xung đột lịch cố định
            if Schedule.objects.filter(
                court=court,
                days=days,
                start_time__lt=end_time_fixed,
                end_time__gt=start_time_fixed,
            ).exclude(id=self.instance.id).exists():
                raise ValidationError("Lịch cố định bị trùng với một lịch đã đặt trước đó.")

        elif schedule_type == 'Daily':
            # Kiểm tra các trường cần thiết cho lịch ngày
            if not date:
                raise ValidationError("Lịch ngày yêu cầu nhập ngày cụ thể.")
            if not start_time_daily or not end_time_daily:
                raise ValidationError("Lịch ngày yêu cầu nhập cả giờ bắt đầu và giờ kết thúc.")

            # Ánh xạ giờ cho lịch ngày
            cleaned_data['start_time'] = start_time_daily
            cleaned_data['end_time'] = end_time_daily

            # Kiểm tra xung đột lịch ngày
            if Schedule.objects.filter(
                court=court,
                date=date,
                start_time__lt=end_time_daily,
                end_time__gt=start_time_daily,
            ).exclude(id=self.instance.id).exists():
                raise ValidationError("Lịch ngày bị trùng với một lịch đã đặt trước đó.")

        elif schedule_type == 'Flexible':
            # Kiểm tra tổng số giờ cho lịch linh hoạt
            if not total_hours or total_hours <= 0:
                raise ValidationError("Lịch linh hoạt yêu cầu nhập tổng số giờ hợp lệ.")

            # Kiểm tra tổng số giờ trong tháng
            if date:
                total_registered_hours = Schedule.objects.filter(
                    customer=self.instance.customer if hasattr(self.instance, 'customer') else None,
                    schedule_type='Flexible',
                    date__year=date.year,
                    date__month=date.month,
                ).aggregate(Sum('total_hours'))['total_hours__sum'] or 0

                if total_registered_hours + total_hours > 100:
                    raise ValidationError(
                        f"Lịch linh hoạt vượt quá giới hạn 100 giờ trong tháng. "
                        f"Đã đăng ký: {total_registered_hours} giờ."
                    )

        return cleaned_data

    def save(self, commit=True):
        schedule = super().save(commit=False)
        if hasattr(self, 'request') and self.request.user:
            schedule.customer = self.request.user
        if commit:
            schedule.save()
        return schedule

    
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['court', 'date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }
