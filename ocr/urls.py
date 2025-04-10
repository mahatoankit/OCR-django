from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_image, name='upload_image'),
    path('my-uploads/', views.my_uploads, name='my_uploads'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),
]