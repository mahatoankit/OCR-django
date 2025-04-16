from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.files.base import ContentFile
from .forms import (
    OCRImageForm,
    OCRDataEditForm,
    CitizenshipFrontForm,
    CitizenshipBackForm,
)
from .models import OcrImage, CitizenshipFront, CitizenshipBack
from .citizenship_ocr import process_citizenship_images, label_citizenship_image
import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import logging

# Set up logging
logger = logging.getLogger(__name__)


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
            front_image = form.cleaned_data["front_image"]
            back_image = form.cleaned_data["back_image"]

            # First, create and save the CitizenshipFront instance
            front_data = CitizenshipFront(user=request.user, front_image=front_image)
            front_data.save()

            # Process front image with OCR
            try:
                # Process the front image
                with front_data.front_image.open("rb") as front_file:
                    # Process the images - gets both English and Nepali data
                    back_file = None
                    if back_image:
                        # Create CitizenshipBack instance if back image is provided
                        back_data = CitizenshipBack(
                            front=front_data, back_image=back_image
                        )
                        back_data.save()
                        back_file = back_data.back_image.open("rb")

                    # Process both images if available
                    extracted_data = process_citizenship_images(front_file, back_file)

                    if back_file:
                        back_file.close()

                # Save raw OCR text as JSON representation for front data
                front_data.text_result = json.dumps(extracted_data, indent=2)

                # Save English structured data to front model
                front_data.full_name_en = extracted_data.get("full_name")
                front_data.father_name_en = extracted_data.get("father_name")
                front_data.mother_name_en = extracted_data.get("mother_name")
                front_data.gender_en = extracted_data.get("gender")
                front_data.citizenship_no_en = extracted_data.get("citizenship_no")
                front_data.dob_en = extracted_data.get("dob")
                front_data.birth_place_en = extracted_data.get("birth_place")
                front_data.permanent_address_en = extracted_data.get(
                    "permanent_address"
                )
                front_data.spouse_name_en = extracted_data.get("spouse_name")

                # Save Nepali structured data to front model
                front_data.full_name_np = extracted_data.get("full_name_np")
                front_data.father_name_np = extracted_data.get("father_name_np")
                front_data.mother_name_np = extracted_data.get("mother_name_np")
                front_data.gender_np = extracted_data.get("gender_np")
                front_data.citizenship_no_np = extracted_data.get("citizenship_no_np")
                front_data.dob_np = extracted_data.get("dob_np")
                front_data.birth_place_np = extracted_data.get("birth_place_np")
                front_data.permanent_address_np = extracted_data.get(
                    "permanent_address_np"
                )
                front_data.spouse_name_np = extracted_data.get("spouse_name_np")

                # Parse the scan date if available
                if "scan_date" in extracted_data:
                    try:
                        front_data.scan_date = datetime.strptime(
                            extracted_data["scan_date"], "%Y-%m-%d"
                        ).date()
                    except ValueError:
                        pass

                # Save back side data if back image was provided
                if back_image and "back_data" in locals():
                    back_data.issue_date_en = extracted_data.get("issue_date")
                    back_data.authority_en = extracted_data.get("authority")
                    back_data.issue_date_np = extracted_data.get("issue_date_np")
                    back_data.authority_np = extracted_data.get("authority_np")
                    back_data.scan_date = front_data.scan_date
                    back_data.save()

                # Create the OcrImage wrapper that links front and optionally back
                ocr_image = OcrImage(
                    user=request.user,
                    front=front_data,
                    text_result=front_data.text_result,
                )

                if back_image and "back_data" in locals():
                    ocr_image.back = back_data

                ocr_image.save()

                # Label images
                try:
                    # Label front image
                    with front_data.front_image.open("rb") as front_file:
                        labeled_front = label_citizenship_image(
                            front_file, is_front=True
                        )
                        front_data.labeled_front_image.save(
                            f"labeled_front_{front_data.id}.png",
                            ContentFile(labeled_front),
                            save=True,
                        )

                    # Label back image if provided
                    if back_image and "back_data" in locals():
                        with back_data.back_image.open("rb") as back_file:
                            labeled_back = label_citizenship_image(
                                back_file, is_front=False
                            )
                            back_data.labeled_back_image.save(
                                f"labeled_back_{back_data.id}.png",
                                ContentFile(labeled_back),
                                save=True,
                            )

                    messages.success(
                        request,
                        "Citizenship card uploaded, processed, and labeled successfully!",
                    )
                except Exception as e:
                    messages.warning(
                        request, f"Images processed but labeling failed: {str(e)}"
                    )
            except Exception as e:
                messages.warning(
                    request, f"Image uploaded but OCR processing failed: {str(e)}"
                )

            return redirect("my_uploads")
    else:
        form = OCRImageForm()

    return render(request, "ocr/upload.html", {"form": form})


@login_required
def my_uploads(request):
    uploads = OcrImage.objects.filter(user=request.user).order_by("-uploaded_at")
    return render(request, "ocr/my_uploads.html", {"uploads": uploads})


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
    front_data = ocr_image.front
    back_data = (
        ocr_image.back if hasattr(ocr_image, "back") and ocr_image.back else None
    )

    if request.method == "POST":
        form = OCRDataEditForm(request.POST)
        if form.is_valid():
            # Update front data with English fields
            front_data.full_name_en = form.cleaned_data["full_name_en"]
            front_data.father_name_en = form.cleaned_data["father_name_en"]
            front_data.mother_name_en = form.cleaned_data["mother_name_en"]
            front_data.gender_en = form.cleaned_data["gender_en"]
            front_data.citizenship_no_en = form.cleaned_data["citizenship_no_en"]
            front_data.dob_en = form.cleaned_data["dob_en"]
            front_data.birth_place_en = form.cleaned_data["birth_place_en"]
            front_data.permanent_address_en = form.cleaned_data["permanent_address_en"]
            front_data.spouse_name_en = form.cleaned_data["spouse_name_en"]

            # Update front data with Nepali fields
            front_data.full_name_np = form.cleaned_data["full_name_np"]
            front_data.father_name_np = form.cleaned_data["father_name_np"]
            front_data.mother_name_np = form.cleaned_data["mother_name_np"]
            front_data.gender_np = form.cleaned_data["gender_np"]
            front_data.citizenship_no_np = form.cleaned_data["citizenship_no_np"]
            front_data.dob_np = form.cleaned_data["dob_np"]
            front_data.birth_place_np = form.cleaned_data["birth_place_np"]
            front_data.permanent_address_np = form.cleaned_data["permanent_address_np"]
            front_data.spouse_name_np = form.cleaned_data["spouse_name_np"]

            # Save front data
            front_data.save()

            # Update back data if available
            if back_data:
                back_data.issue_date_en = form.cleaned_data["issue_date_en"]
                back_data.authority_en = form.cleaned_data["authority_en"]
                back_data.issue_date_np = form.cleaned_data["issue_date_np"]
                back_data.authority_np = form.cleaned_data["authority_np"]
                back_data.save()

            # Update JSON text result to reflect the changes
            data = {
                # Front - English data
                "full_name": form.cleaned_data["full_name_en"],
                "father_name": form.cleaned_data["father_name_en"],
                "mother_name": form.cleaned_data["mother_name_en"],
                "gender": form.cleaned_data["gender_en"],
                "citizenship_no": form.cleaned_data["citizenship_no_en"],
                "dob": form.cleaned_data["dob_en"],
                "birth_place": form.cleaned_data["birth_place_en"],
                "permanent_address": form.cleaned_data["permanent_address_en"],
                "spouse_name": form.cleaned_data["spouse_name_en"],
                # Back - English data
                "issue_date": form.cleaned_data["issue_date_en"],
                "authority": form.cleaned_data["authority_en"],
                # Front - Nepali data
                "full_name_np": form.cleaned_data["full_name_np"],
                "father_name_np": form.cleaned_data["father_name_np"],
                "mother_name_np": form.cleaned_data["mother_name_np"],
                "gender_np": form.cleaned_data["gender_np"],
                "citizenship_no_np": form.cleaned_data["citizenship_no_np"],
                "dob_np": form.cleaned_data["dob_np"],
                "birth_place_np": form.cleaned_data["birth_place_np"],
                "permanent_address_np": form.cleaned_data["permanent_address_np"],
                "spouse_name_np": form.cleaned_data["spouse_name_np"],
                # Back - Nepali data
                "issue_date_np": form.cleaned_data["issue_date_np"],
                "authority_np": form.cleaned_data["authority_np"],
                # Additional data
                "scan_date": (
                    front_data.scan_date.strftime("%Y-%m-%d")
                    if front_data.scan_date
                    else datetime.now().strftime("%Y-%m-%d")
                ),
            }

            # Update OcrImage text_result
            ocr_image.text_result = json.dumps(data, indent=2)
            ocr_image.save()

            messages.success(request, "Citizenship data updated successfully")
            return redirect("admin_dashboard")
    else:
        # Prepare initial data for the form
        initial_data = {
            # Front - English data
            "full_name_en": front_data.full_name_en,
            "father_name_en": front_data.father_name_en,
            "mother_name_en": front_data.mother_name_en,
            "gender_en": front_data.gender_en,
            "citizenship_no_en": front_data.citizenship_no_en,
            "dob_en": front_data.dob_en,
            "birth_place_en": front_data.birth_place_en,
            "permanent_address_en": front_data.permanent_address_en,
            "spouse_name_en": front_data.spouse_name_en,
            # Front - Nepali data
            "full_name_np": front_data.full_name_np,
            "father_name_np": front_data.father_name_np,
            "mother_name_np": front_data.mother_name_np,
            "gender_np": front_data.gender_np,
            "citizenship_no_np": front_data.citizenship_no_np,
            "dob_np": front_data.dob_np,
            "birth_place_np": front_data.birth_place_np,
            "permanent_address_np": front_data.permanent_address_np,
            "spouse_name_np": front_data.spouse_name_np,
        }

        # Add back data if available
        if back_data:
            initial_data.update(
                {
                    "issue_date_en": back_data.issue_date_en,
                    "authority_en": back_data.authority_en,
                    "issue_date_np": back_data.issue_date_np,
                    "authority_np": back_data.authority_np,
                }
            )

        form = OCRDataEditForm(initial=initial_data)

    # Pass both front and back images to the template
    context = {
        "form": form,
        "image": ocr_image,
        "front_data": front_data,
        "back_data": back_data,
    }

    return render(request, "ocr/edit_ocr_data.html", context)


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
