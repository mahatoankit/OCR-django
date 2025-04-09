from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import OCRImageForm
from .models import OcrImage
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login



def home(request):
    """Redirect to appropriate page based on authentication status"""
    if request.user.is_authenticated:
        return redirect('my_uploads')
    return redirect('login')

def is_admin(user):
    """Check if user is staff"""
    return user.is_staff

@login_required
def upload_image(request):
    """View for users to upload images"""
    if request.method == 'POST':
        form = OCRImageForm(request.POST, request.FILES)
        if form.is_valid():
            ocr_image = form.save(commit=False)
            ocr_image.user = request.user
            
            # Here you could add OCR processing logic
            # For now, just save the image
            ocr_image.save()
            messages.success(request, 'Image uploaded successfully!')
            return redirect('my_uploads')
    else:
        form = OCRImageForm()
    
    return render(request, 'ocr/upload.html', {'form': form})

@login_required
def my_uploads(request):
    """View for users to see their uploads"""
    uploads = OcrImage.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'ocr/my_uploads.html', {'uploads': uploads})

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin view to see all uploads"""
    all_uploads = OcrImage.objects.all().order_by('-uploaded_at')
    return render(request, 'ocr/admin_dashboard.html', {'uploads': all_uploads})

from django.contrib.auth import logout

def logout_view(request):
    """Logout view"""
    logout(request)
    return redirect('landing_page')

# Add this function if it doesn't exist already
def landing_page(request):
    """Landing page view"""
    if request.user.is_authenticated:
        return redirect('my_uploads')
    return render(request, 'landing.html')



# Add this function to your views.py
def signup_view(request):
    """Sign up view"""
    if request.user.is_authenticated:
        return redirect('my_uploads')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('my_uploads')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})