from django.db import models
from django.contrib.auth.models import User

class OcrImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='ocr_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Raw OCR text result
    text_result = models.TextField(blank=True, null=True)
    
    # Structured citizenship data
    full_name = models.CharField(max_length=100, blank=True, null=True)
    father_name = models.CharField(max_length=100, blank=True, null=True)
    mother_name = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    citizenship_no = models.CharField(max_length=50, blank=True, null=True)
    dob = models.CharField(max_length=50, blank=True, null=True)
    birth_place = models.CharField(max_length=100, blank=True, null=True)
    permanent_address = models.CharField(max_length=200, blank=True, null=True)
    spouse_name = models.CharField(max_length=100, blank=True, null=True)
    issue_date = models.CharField(max_length=50, blank=True, null=True)
    authority = models.CharField(max_length=100, blank=True, null=True)
    scan_date = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return f"Citizenship scan by {self.user.username} ({self.uploaded_at.strftime('%Y-%m-%d %H:%M')})"