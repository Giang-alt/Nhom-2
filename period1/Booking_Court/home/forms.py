
from django import forms
from B_Court_Mng.models import Court

class CourtNewForm(forms.ModelForm):
    class Meta:
        model = Court
        fields = ['CourtName', 'Location', 'OpeningHours', 'ClosingHours', 'Active', 'CourtType', 'WeekdayPrice', 'WeekendPrice'] 
        widgets = {
            'OpeningHours': forms.TimeInput(format='%H:%M'),
            'ClosingHours': forms.TimeInput(format='%H:%M'),
        }

from django.contrib.auth.models import User

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

