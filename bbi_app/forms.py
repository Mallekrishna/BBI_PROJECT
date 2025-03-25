from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import DriverProfile, DrivingTrip

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name']

class DriverProfileForm(forms.ModelForm):
    class Meta:
        model = DriverProfile
        fields = ['policy_number', 'phone_number', 'device_id']
        widgets = {
            'policy_number': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'device_id': forms.TextInput(attrs={'class': 'form-control'}),
        }

class TripUploadForm(forms.Form):
    trip_data = forms.FileField(label='Upload Trip Data (CSV)')
    
    def clean_trip_data(self):
        data = self.cleaned_data['trip_data']
        if not data.name.endswith('.csv'):
            raise forms.ValidationError('Only CSV files are accepted')
        return data