from django import forms
from .models import OcrImage

class OCRImageForm(forms.ModelForm):
    class Meta:
        model = OcrImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
        }
        labels = {
            'image': 'Select Citizenship Card Image'
        }
        help_texts = {
            'image': 'Upload a clear image of the Nepali citizenship card.'
        }