from django import forms
from .models import OcrImage

class OCRImageForm(forms.ModelForm):
    class Meta:
        model = OcrImage
        fields = ['image']