from django.urls import path
from . import views

urlpatterns = [
    path("upload/", views.upload_image, name="upload_image"),
    path("my-uploads/", views.my_uploads, name="my_uploads"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("edit/<int:image_id>/", views.edit_ocr_data, name="edit_ocr_data"),
    # Fix the name to match the view function
    path("delete/<int:image_id>/", views.delete_ocr_image, name="delete_ocr_image"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.home, name="home"),
]