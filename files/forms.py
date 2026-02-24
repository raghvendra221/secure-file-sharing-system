from django import forms
from .models import SecureFile  
class FileUploadForm(forms.ModelForm):
    class Meta:
        model = SecureFile
        fields = ['file']