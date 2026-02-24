from django import forms
from .models import SecureFile  
class FileUploadForm(forms.ModelForm):
    class Meta:
        model = SecureFile
        fields = ['file']

        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }

        
class ShareTokenForm(forms.Form):
    expiry_minutes = forms.IntegerField(
        min_value=1,
        label="Expiry (in minutes)",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    max_downloads = forms.IntegerField(
        min_value=1,
        label="Max Downloads",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )