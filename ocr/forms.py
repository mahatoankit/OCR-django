from django import forms
from .models import CitizenshipFront, CitizenshipBack, OcrImage


class CitizenshipFrontForm(forms.ModelForm):
    class Meta:
        model = CitizenshipFront
        fields = ["front_image"]
        widgets = {
            "front_image": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
        }
        labels = {
            "front_image": "Front Side of Citizenship Card",
        }
        help_texts = {
            "front_image": "Upload a clear image of the front side.",
        }


class CitizenshipBackForm(forms.ModelForm):
    class Meta:
        model = CitizenshipBack
        fields = ["back_image"]
        widgets = {
            "back_image": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
        }
        labels = {
            "back_image": "Back Side of Citizenship Card (Optional)",
        }
        help_texts = {
            "back_image": "Upload the back side for complete information (recommended).",
        }


class OCRImageForm(forms.Form):
    """Combined form for uploading both front and back images"""

    front_image = forms.ImageField(
        widget=forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
        label="Front Side of Citizenship Card",
        help_text="Upload a clear image of the front side.",
    )
    back_image = forms.ImageField(
        widget=forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
        label="Back Side of Citizenship Card (Optional)",
        help_text="Upload the back side for complete information (recommended).",
        required=False,
    )


class CitizenshipFrontEditForm(forms.ModelForm):
    """Form for editing front side data"""

    class Meta:
        model = CitizenshipFront
        fields = [
            # English fields
            "full_name_en",
            "father_name_en",
            "mother_name_en",
            "gender_en",
            "citizenship_no_en",
            "dob_en",
            "birth_place_en",
            "permanent_address_en",
            "spouse_name_en",
            # Nepali fields
            "full_name_np",
            "father_name_np",
            "mother_name_np",
            "gender_np",
            "citizenship_no_np",
            "dob_np",
            "birth_place_np",
            "permanent_address_np",
            "spouse_name_np",
        ]
        widgets = {
            # English fields
            "citizenship_no_en": forms.TextInput(attrs={"class": "form-control"}),
            "full_name_en": forms.TextInput(attrs={"class": "form-control"}),
            "father_name_en": forms.TextInput(attrs={"class": "form-control"}),
            "mother_name_en": forms.TextInput(attrs={"class": "form-control"}),
            "gender_en": forms.Select(
                attrs={"class": "form-control"},
                choices=[
                    ("", "------"),
                    ("Male", "Male"),
                    ("Female", "Female"),
                    ("Other", "Other"),
                ],
            ),
            "dob_en": forms.TextInput(attrs={"class": "form-control"}),
            "birth_place_en": forms.TextInput(attrs={"class": "form-control"}),
            "permanent_address_en": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "spouse_name_en": forms.TextInput(attrs={"class": "form-control"}),
            # Nepali fields
            "citizenship_no_np": forms.TextInput(
                attrs={"class": "form-control", "dir": "auto"}
            ),
            "full_name_np": forms.TextInput(
                attrs={"class": "form-control", "dir": "auto"}
            ),
            "father_name_np": forms.TextInput(
                attrs={"class": "form-control", "dir": "auto"}
            ),
            "mother_name_np": forms.TextInput(
                attrs={"class": "form-control", "dir": "auto"}
            ),
            "gender_np": forms.TextInput(
                attrs={"class": "form-control", "dir": "auto"}
            ),
            "dob_np": forms.TextInput(attrs={"class": "form-control", "dir": "auto"}),
            "birth_place_np": forms.TextInput(
                attrs={"class": "form-control", "dir": "auto"}
            ),
            "permanent_address_np": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "dir": "auto"}
            ),
            "spouse_name_np": forms.TextInput(
                attrs={"class": "form-control", "dir": "auto"}
            ),
        }


class CitizenshipBackEditForm(forms.ModelForm):
    """Form for editing back side data"""

    class Meta:
        model = CitizenshipBack
        fields = [
            # English fields
            "issue_date_en",
            "authority_en",
            # Nepali fields
            "issue_date_np",
            "authority_np",
        ]
        widgets = {
            # English fields
            "issue_date_en": forms.TextInput(attrs={"class": "form-control"}),
            "authority_en": forms.TextInput(attrs={"class": "form-control"}),
            # Nepali fields
            "issue_date_np": forms.TextInput(
                attrs={"class": "form-control", "dir": "auto"}
            ),
            "authority_np": forms.TextInput(
                attrs={"class": "form-control", "dir": "auto"}
            ),
        }


class OCRDataEditForm(forms.Form):
    """Combined form for editing both front and back data"""

    # Front side - English fields
    citizenship_no_en = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Citizenship Number",
    )
    full_name_en = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Full Name",
    )
    father_name_en = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Father's Name",
    )
    mother_name_en = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Mother's Name",
    )
    gender_en = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        choices=[
            ("", "------"),
            ("Male", "Male"),
            ("Female", "Female"),
            ("Other", "Other"),
        ],
        label="Gender",
    )
    dob_en = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Date of Birth",
    )
    birth_place_en = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Birth Place",
    )
    permanent_address_en = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        label="Permanent Address",
    )
    spouse_name_en = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Spouse's Name",
    )

    # Back side - English fields
    issue_date_en = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Issue Date",
    )
    authority_en = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Issuing Authority",
    )

    # Front side - Nepali fields
    citizenship_no_np = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "dir": "auto"}),
        label="Citizenship Number (Nepali)",
    )
    full_name_np = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "dir": "auto"}),
        label="Full Name (Nepali)",
    )
    father_name_np = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "dir": "auto"}),
        label="Father's Name (Nepali)",
    )
    mother_name_np = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "dir": "auto"}),
        label="Mother's Name (Nepali)",
    )
    gender_np = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "dir": "auto"}),
        label="Gender (Nepali)",
    )
    dob_np = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "dir": "auto"}),
        label="Date of Birth (Nepali)",
    )
    birth_place_np = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "dir": "auto"}),
        label="Birth Place (Nepali)",
    )
    permanent_address_np = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 3, "dir": "auto"}
        ),
        label="Permanent Address (Nepali)",
    )
    spouse_name_np = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "dir": "auto"}),
        label="Spouse's Name (Nepali)",
    )

    # Back side - Nepali fields
    issue_date_np = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "dir": "auto"}),
        label="Issue Date (Nepali)",
    )
    authority_np = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "dir": "auto"}),
        label="Issuing Authority (Nepali)",
    )
