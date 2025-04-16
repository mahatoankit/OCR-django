from django.db import models
from django.contrib.auth.models import User

class CitizenshipFront(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    front_image = models.ImageField(upload_to="ocr_images/")
    labeled_front_image = models.ImageField(upload_to="labeled_images/", blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    text_result = models.TextField(blank=True, null=True)
    # English fields
    full_name_en = models.CharField(max_length=255, blank=True, null=True)
    father_name_en = models.CharField(max_length=255, blank=True, null=True)
    mother_name_en = models.CharField(max_length=255, blank=True, null=True)
    gender_en = models.CharField(max_length=50, blank=True, null=True)
    citizenship_no_en = models.CharField(max_length=100, blank=True, null=True)
    dob_en = models.CharField(max_length=100, blank=True, null=True)
    birth_place_en = models.CharField(max_length=255, blank=True, null=True)
    permanent_address_en = models.TextField(blank=True, null=True)
    spouse_name_en = models.CharField(max_length=255, blank=True, null=True)
    # Nepali fields
    full_name_np = models.CharField(max_length=255, blank=True, null=True)
    father_name_np = models.CharField(max_length=255, blank=True, null=True)
    mother_name_np = models.CharField(max_length=255, blank=True, null=True)
    gender_np = models.CharField(max_length=50, blank=True, null=True)
    citizenship_no_np = models.CharField(max_length=100, blank=True, null=True)
    dob_np = models.CharField(max_length=100, blank=True, null=True)
    birth_place_np = models.CharField(max_length=255, blank=True, null=True)
    permanent_address_np = models.TextField(blank=True, null=True)
    spouse_name_np = models.CharField(max_length=255, blank=True, null=True)
    scan_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Front: {self.full_name_en or self.full_name_np} ({self.citizenship_no_en or self.citizenship_no_np})"

class CitizenshipBack(models.Model):
    front = models.OneToOneField(CitizenshipFront, on_delete=models.CASCADE, related_name="back")
    back_image = models.ImageField(upload_to="ocr_images/")
    labeled_back_image = models.ImageField(upload_to="labeled_images/", blank=True, null=True)
    # English fields
    issue_date_en = models.CharField(max_length=100, blank=True, null=True)
    authority_en = models.CharField(max_length=255, blank=True, null=True)
    # Nepali fields
    issue_date_np = models.CharField(max_length=100, blank=True, null=True)
    authority_np = models.CharField(max_length=255, blank=True, null=True)
    scan_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Back: {self.authority_en or self.authority_np} ({self.issue_date_en or self.issue_date_np})"

# Optionally, you can keep OcrImage as a wrapper for upload tracking, or remove it if not needed.
# Remove all structured data fields from OcrImage, and instead reference the new models.
class OcrImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    front = models.OneToOneField(CitizenshipFront, on_delete=models.CASCADE, related_name="ocr_image", null=True)
    back = models.OneToOneField(CitizenshipBack, on_delete=models.SET_NULL, blank=True, null=True, related_name="ocr_image")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    text_result = models.TextField(blank=True, null=True)
    # Flag to mark as migrated - for migration script use
    is_migrated = models.BooleanField(default=False)

    def __str__(self):
        if self.front:
            return f"OCR Upload: {self.front.citizenship_no_en or 'Unknown'}"
        return f"OCR Upload by {self.user.username} at {self.uploaded_at}"
        
    # Method for templates to get front image URL
    def get_front_image_url(self):
        if self.front and self.front.front_image:
            return self.front.front_image.url
        return None
        
    # Method for templates to get back image URL
    def get_back_image_url(self):
        if self.back and self.back.back_image:
            return self.back.back_image.url
        return None
        
    # For back-compatibility with templates
    def has_back_image(self):
        return self.back is not None
