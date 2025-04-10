from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.files.base import ContentFile
from .forms import OCRImageForm, OCRDataEditForm
from .models import OcrImage
from .citizenship_ocr import process_citizenship_images, label_citizenship_image
import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont


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
    """View for users to upload citizenship images (both sides)"""
    if request.method == "POST":
        form = OCRImageForm(request.POST, request.FILES)
        if form.is_valid():
            ocr_image = form.save(commit=False)
            ocr_image.user = request.user

            # First save the model to store the images
            ocr_image.save()

            # Now process the images with OCR
            try:
                # Reopen the saved files for processing
                with ocr_image.front_image.open("rb") as front_file:
                    # Check if back image is provided
                    back_file = None
                    if ocr_image.back_image:
                        back_file = ocr_image.back_image.open("rb")

                    # Process the images
                    extracted_data = process_citizenship_images(front_file, back_file)

                    if back_file:
                        back_file.close()

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

                # Generate labeled images
                try:
                    # Label front image
                    with ocr_image.front_image.open("rb") as front_file:
                        labeled_front = label_citizenship_image(
                            front_file, is_front=True
                        )
                        ocr_image.labeled_front_image.save(
                            f"labeled_front_{ocr_image.id}.png",
                            ContentFile(labeled_front),
                            save=False,
                        )

                    # Label back image if provided
                    if ocr_image.back_image:
                        with ocr_image.back_image.open("rb") as back_file:
                            labeled_back = label_citizenship_image(
                                back_file, is_front=False
                            )
                            ocr_image.labeled_back_image.save(
                                f"labeled_back_{ocr_image.id}.png",
                                ContentFile(labeled_back),
                                save=False,
                            )

                    ocr_image.save()
                    messages.success(
                        request,
                        "Citizenship card uploaded, processed, and labeled successfully!",
                    )
                except Exception as e:
                    ocr_image.save()
                    messages.warning(
                        request, f"Images processed but labeling failed: {str(e)}"
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
    uploads = OcrImage.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'ocr/my_uploads.html', {'uploads': uploads})


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin view to see all uploads"""
    all_uploads = OcrImage.objects.all().order_by("-uploaded_at")
    return render(request, "ocr/admin_dashboard.html", {"uploads": all_uploads})


@login_required
@user_passes_test(is_admin)
def edit_ocr_data(request, image_id):
    """Admin view to edit OCR data"""
    ocr_image = get_object_or_404(OcrImage, id=image_id)

    if request.method == "POST":
        form = OCRDataEditForm(request.POST, instance=ocr_image)
        if form.is_valid():
            # Save the form
            form.save()

            # Update the JSON text_result to reflect the changes
            data = {
                "full_name": form.cleaned_data["full_name"],
                "father_name": form.cleaned_data["father_name"],
                "mother_name": form.cleaned_data["mother_name"],
                "gender": form.cleaned_data["gender"],
                "citizenship_no": form.cleaned_data["citizenship_no"],
                "dob": form.cleaned_data["dob"],
                "birth_place": form.cleaned_data["birth_place"],
                "permanent_address": form.cleaned_data["permanent_address"],
                "spouse_name": form.cleaned_data["spouse_name"],
                "issue_date": form.cleaned_data["issue_date"],
                "authority": form.cleaned_data["authority"],
                "scan_date": (
                    ocr_image.scan_date.strftime("%Y-%m-%d")
                    if ocr_image.scan_date
                    else datetime.now().strftime("%Y-%m-%d")
                ),
            }

            ocr_image.text_result = json.dumps(data, indent=2)
            ocr_image.save()

            messages.success(request, "Citizenship data updated successfully")
            return redirect("admin_dashboard")
    else:
        form = OCRDataEditForm(instance=ocr_image)

    return render(request, "ocr/edit_ocr_data.html", {"form": form, "image": ocr_image})


@login_required
@user_passes_test(is_admin)
def delete_ocr_image(request, image_id):
    """Admin view to delete OCR image"""
    ocr_image = get_object_or_404(OcrImage, id=image_id)

    if request.method == "POST":
        # Delete the image and all associated files
        ocr_image.delete()
        messages.success(request, "Citizenship data deleted successfully")
        return redirect("admin_dashboard")

    return render(request, "ocr/confirm_delete.html", {"image": ocr_image})


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
