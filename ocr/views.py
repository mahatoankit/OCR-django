from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import OCRImageForm
from .models import OcrImage
from .citizenship_ocr import process_citizenship_image
import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout



def home(request):
    """Redirect to appropriate page based on authentication status"""
    if request.user.is_authenticated:
        return redirect("my_uploads")
    return redirect("login")


def is_admin(user):
    """Check if user is staff"""
    return user.is_staff


@login_required
def upload_image(request):
    """View for users to upload citizenship images"""
    if request.method == "POST":
        form = OCRImageForm(request.POST, request.FILES)
        if form.is_valid():
            ocr_image = form.save(commit=False)
            ocr_image.user = request.user

            # Process the image with Gemini OCR
            try:
                extracted_data = process_citizenship_image(request.FILES["image"])

                # Save raw OCR text as JSON representation
                ocr_image.text_result = json.dumps(extracted_data, indent=2)

                # Save structured data
                ocr_image.full_name = extracted_data.get("full_name")
                ocr_image.father_name = extracted_data.get("father_name")
                ocr_image.mother_name = extracted_data.get("mother_name")
                ocr_image.gender = extracted_data.get("gender")
                ocr_image.citizenship_no = extracted_data.get("citizenship_no")
                ocr_image.dob = extracted_data.get("dob")
                ocr_image.birth_place = extracted_data.get("birth_place")
                ocr_image.permanent_address = extracted_data.get("permanent_address")
                ocr_image.spouse_name = extracted_data.get("spouse_name")
                ocr_image.issue_date = extracted_data.get("issue_date")
                ocr_image.authority = extracted_data.get("authority")

                # Parse the scan date if available
                if "scan_date" in extracted_data:
                    try:
                        ocr_image.scan_date = datetime.strptime(
                            extracted_data["scan_date"], "%Y-%m-%d"
                        ).date()
                    except ValueError:
                        pass

                ocr_image.save()
                messages.success(
                    request, "Citizenship card uploaded and processed successfully!"
                )
            except Exception as e:
                ocr_image.save()  # Save even if OCR fails
                messages.warning(
                    request, f"Image uploaded but OCR processing failed: {str(e)}"
                )

            return redirect("my_uploads")
    else:
        form = OCRImageForm()

    return render(request, "ocr/upload.html", {"form": form})


@login_required
def my_uploads(request):
    """View for users to see their uploads"""
    uploads = OcrImage.objects.filter(user=request.user).order_by("-uploaded_at")
    return render(request, "ocr/my_uploads.html", {"uploads": uploads})


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin view to see all uploads"""
    all_uploads = OcrImage.objects.all().order_by("-uploaded_at")
    return render(request, "ocr/admin_dashboard.html", {"uploads": all_uploads})


def logout_view(request):
    """Logout view"""
    logout(request)
    return redirect("landing_page")


# Add this function if it doesn't exist already
def landing_page(request):
    """Landing page view"""
    if request.user.is_authenticated:
        return redirect("my_uploads")
    return render(request, "landing.html")


# Add this function to your views.py
def signup_view(request):
    """Sign up view"""
    if request.user.is_authenticated:
        return redirect("my_uploads")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("my_uploads")
    else:
        form = UserCreationForm()

    return render(request, "registration/signup.html", {"form": form})
