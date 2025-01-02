from django import forms

class CourtNewForm(forms.Form):
    CourtName = forms.CharField(label="CourtName", max_length = 100)
    Location = forms.CharField(label="Location", max_length = 100)
    OpeningHours = forms.TimeField(label="OpeningHours")
    ClosingHours = forms.TimeField(label="ClosingHours")
    Active = forms.BooleanField(label="Active")
