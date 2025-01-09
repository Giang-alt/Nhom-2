
from django import forms
from B_Court_Mng.models import Court

class CourtNewForm(forms.ModelForm):
    class Meta:
        model = Court
        fields = ['CourtName', 'Location', 'OpeningHours', 'ClosingHours', 'Active', 'CourtType', 'Price']  # Đảm bảo có CourtType
        widgets = {
            'OpeningHours': forms.TimeInput(format='%H:%M'),
            'ClosingHours': forms.TimeInput(format='%H:%M'),
        }