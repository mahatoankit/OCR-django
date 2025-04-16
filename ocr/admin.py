from django.contrib import admin
from .models import OcrImage, CitizenshipFront, CitizenshipBack

@admin.register(CitizenshipFront)
class CitizenshipFrontAdmin(admin.ModelAdmin):
    list_display = ('user', 'citizenship_no_en', 'full_name_en', 'uploaded_at')
    list_filter = ('uploaded_at', 'user')
    search_fields = ('user__username', 'citizenship_no_en', 'citizenship_no_np', 'full_name_en', 'full_name_np')
    readonly_fields = ('text_result', 'scan_date', 'uploaded_at')
    fieldsets = (
        ('Images', {
            'fields': ('front_image', 'labeled_front_image')
        }),
        ('English Data', {
            'fields': ('citizenship_no_en', 'full_name_en', 'father_name_en', 'mother_name_en', 
                       'gender_en', 'dob_en', 'birth_place_en', 'permanent_address_en', 'spouse_name_en')
        }),
        ('Nepali Data', {
            'fields': ('citizenship_no_np', 'full_name_np', 'father_name_np', 'mother_name_np', 
                       'gender_np', 'dob_np', 'birth_place_np', 'permanent_address_np', 'spouse_name_np')
        }),
        ('Metadata', {
            'fields': ('user', 'uploaded_at', 'scan_date', 'text_result')
        }),
    )

@admin.register(CitizenshipBack)
class CitizenshipBackAdmin(admin.ModelAdmin):
    list_display = ('front', 'issue_date_en', 'authority_en')
    search_fields = ('front__citizenship_no_en', 'authority_en', 'authority_np')
    readonly_fields = ('scan_date',)
    fieldsets = (
        ('Images', {
            'fields': ('back_image', 'labeled_back_image')
        }),
        ('English Data', {
            'fields': ('issue_date_en', 'authority_en')
        }),
        ('Nepali Data', {
            'fields': ('issue_date_np', 'authority_np')
        }),
        ('Metadata', {
            'fields': ('front', 'scan_date')
        }),
    )

@admin.register(OcrImage)
class OcrImageAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_citizenship_no', 'get_full_name', 'uploaded_at')
    list_filter = ('uploaded_at', 'user')
    search_fields = ('user__username', 'front__citizenship_no_en', 'front__full_name_en')
    readonly_fields = ('text_result', 'uploaded_at')
    
    def get_citizenship_no(self, obj):
        return obj.front.citizenship_no_en if obj.front else "-"
    get_citizenship_no.short_description = 'Citizenship #'
    
    def get_full_name(self, obj):
        return obj.front.full_name_en if obj.front else "-"
    get_full_name.short_description = 'Full Name'