from django.contrib import admin
from .models import OcrImage

@admin.register(OcrImage)
class OcrImageAdmin(admin.ModelAdmin):
    list_display = ('user', 'citizenship_no', 'full_name', 'uploaded_at')
    list_filter = ('uploaded_at', 'user')
    search_fields = ('user__username', 'citizenship_no', 'full_name', 'father_name', 'mother_name')
    readonly_fields = ('text_result', 'scan_date', 'uploaded_at')