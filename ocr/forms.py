from django import forms
from .models import OcrImage


class OCRImageForm(forms.ModelForm):
    class Meta:
        model = OcrImage
        fields = ["front_image", "back_image"]
        widgets = {
            "front_image": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "back_image": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
        }
        labels = {
            "front_image": "Front Side of Citizenship Card",
            "back_image": "Back Side of Citizenship Card (Optional)",
        }
        help_texts = {
            "front_image": "Upload a clear image of the front side.",
            "back_image": "Upload the back side for complete information (recommended).",
        }


class OCRDataEditForm(forms.ModelForm):
    """Form for editing OCR data by admin"""

    class Meta:
        model = OcrImage
        fields = [
            "citizenship_no",
            "full_name",
            "father_name",
            "mother_name",
            "gender",
            "dob",
            "birth_place",
            "permanent_address",
            "spouse_name",
            "issue_date",
            "authority",
        ]
        widgets = {
            "citizenship_no": forms.TextInput(attrs={"class": "form-control"}),
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "father_name": forms.TextInput(attrs={"class": "form-control"}),
            "mother_name": forms.TextInput(attrs={"class": "form-control"}),
            "gender": forms.Select(
                attrs={"class": "form-control"},
                choices=[
                    ("", "------"),
                    ("Male", "Male"),
                    ("Female", "Female"),
                    ("Other", "Other"),
                ],
            ),
            "dob": forms.TextInput(attrs={"class": "form-control"}),
            "birth_place": forms.TextInput(attrs={"class": "form-control"}),
            "permanent_address": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "spouse_name": forms.TextInput(attrs={"class": "form-control"}),
            "issue_date": forms.TextInput(attrs={"class": "form-control"}),
            "authority": forms.TextInput(attrs={"class": "form-control"}),
        }
