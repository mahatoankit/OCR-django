from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class OcrImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='ocr_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    text_result = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Image by {self.user.username} ({self.uploaded_at.strftime('%Y-%m-%d %H:%M') if self.uploaded_at else 'No date'})"
    