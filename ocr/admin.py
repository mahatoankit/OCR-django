from django.contrib import admin
from .models import OcrImage

@admin.register(OcrImage)
class OcrImageAdmin(admin.ModelAdmin):
    list_display = ('user', 'uploaded_at', 'image')
    list_filter = ('uploaded_at', 'user')
    search_fields = ('user__username', 'text_result')