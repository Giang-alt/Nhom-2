from django import forms
from B_Court_Mng.models import Court, Schedule
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models import Sum

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

        # Extract times from input fields
        start_time_fixed = cleaned_data.get('start_time_fixed')
        end_time_fixed = cleaned_data.get('end_time_fixed')
        start_time_daily = cleaned_data.get('start_time_daily')
        end_time_daily = cleaned_data.get('end_time_daily')

        if schedule_type == 'Fixed':
            # Validation for fixed schedule
            if not days:
                raise ValidationError("Fixed schedule requires selecting at least one day.")
            if not start_time_fixed or not end_time_fixed:
                raise ValidationError("Fixed schedule requires both start and end times.")

            # Map times for fixed schedule
            cleaned_data['start_time'] = start_time_fixed
            cleaned_data['end_time'] = end_time_fixed

            # Conflict check for fixed schedule
            if Schedule.objects.filter(
                court=court,
                days=days,
                start_time__lt=end_time_fixed,
                end_time__gt=start_time_fixed,
            ).exclude(id=self.instance.id).exists():
                raise ValidationError("Fixed schedule conflicts with an existing schedule.")

        elif schedule_type == 'Daily':
            # Validation for daily schedule
            if not date:
                raise ValidationError("Daily schedule requires a specific date.")
            if not start_time_daily or not end_time_daily:
                raise ValidationError("Daily schedule requires both start and end times.")

            # Map times for daily schedule
            cleaned_data['start_time'] = start_time_daily
            cleaned_data['end_time'] = end_time_daily

            # Conflict check for daily schedule
            if Schedule.objects.filter(
                court=court,
                date=date,
                start_time__lt=end_time_daily,
                end_time__gt=start_time_daily,
            ).exclude(id=self.instance.id).exists():
                raise ValidationError("Daily schedule conflicts with an existing schedule.")

        elif schedule_type == 'Flexible':
            # Validation for flexible schedule
            if not total_hours or total_hours <= 0:
                raise ValidationError("Flexible schedule requires a valid total hours entry.")

            # Total hours check for the month
            if date:
                total_registered_hours = Schedule.objects.filter(
                    customer=self.instance.customer if hasattr(self.instance, 'customer') else None,
                    schedule_type='Flexible',
                    date__year=date.year,
                    date__month=date.month,
                ).aggregate(Sum('total_hours'))['total_hours__sum'] or 0

                if total_registered_hours + total_hours > 100:
                    raise ValidationError(
                        f"Flexible schedule exceeds the 100-hour limit for the month. "
                        f"Already registered: {total_registered_hours} hours."
                    )

        return cleaned_data

    def save(self, commit=True):
        schedule = super().save(commit=False)
        if hasattr(self, 'request') and self.request.user:
            schedule.customer = self.request.user
        if commit:
            schedule.save()
        return schedule
