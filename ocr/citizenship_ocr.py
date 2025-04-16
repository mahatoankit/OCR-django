import os
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import io
import json
import cv2
import numpy as np
from datetime import datetime

# Configure Gemini
genai.configure(api_key="AIzaSyCotnndBVRVBcGlHUiKbP_I_mTmAr1Ages")
model = genai.GenerativeModel("gemini-2.0-flash")


def preprocess_image(image_file):
    """Preprocess image for better OCR results"""
    # Read the image into memory
    img_bytes = image_file.read()
    image_file.seek(0)  # Reset file pointer

    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError(
            "Failed to decode image. The file may be corrupted or in an unsupported format."
        )

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # Noise removal using morphological operations
    kernel = np.ones((1, 1), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    # Edge enhancement
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    enhanced = cv2.addWeighted(gray, 0.7, edges, 0.3, 0)

    # Convert back to RGB
    enhanced_rgb = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)

    # Convert to PIL image and then to bytes
    pil_img = Image.fromarray(enhanced_rgb)
    img_byte_arr = io.BytesIO()
    pil_img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    return img_byte_arr.getvalue()


def label_citizenship_image(image_file, is_front=True):
    """Label the citizenship image with field annotations"""
    # Make a copy of the file in memory to preserve the original
    img_bytes = image_file.read()
    image_file.seek(0)  # Reset file pointer

    # Verify image data is not empty
    if not img_bytes:
        raise ValueError("Empty image data received")

    # Decode with OpenCV
    nparr = np.frombuffer(img_bytes, np.uint8)
    img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img_cv is None:
        raise ValueError(
            "Failed to decode image for labeling. The file may be corrupted."
        )

    # Apply basic preprocessing
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    img_cv = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)

    img = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)

    # Get image dimensions
    width, height = img.size

    # Use adaptive field positions
    if is_front:
        field_positions = calculate_field_positions(width, height)
    else:
        field_positions = calculate_back_field_positions(width, height)

    # Try to use a specific font, fall back to default if unavailable
    try:
        # Check common font paths
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/TTF/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf",
        ]

        font = None
        for path in font_paths:
            if os.path.exists(path):
                font = ImageFont.truetype(path, 16)
                break

        if font is None:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    # Draw the field boxes and labels
    for field_name, positions in field_positions.items():
        # Draw rectangle
        draw.rectangle(
            [positions["box_start"], positions["box_end"]], outline=(0, 200, 0), width=2
        )

        # Add text label
        draw.text(positions["label_pos"], field_name, fill=(255, 0, 0), font=font)

    # Convert to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    return img_byte_arr.getvalue()


def calculate_field_positions(width, height):
    """Calculate adaptive positions for front side fields."""
    # Scale factors based on image dimensions
    x_scale = width / 1600  # Base width assumption
    y_scale = height / 1200  # Base height assumption

    return {
        "Full Name": {
            "label_pos": (int(410 * x_scale), int(360 * y_scale)),
            "box_start": (int(410 * x_scale), int(380 * y_scale)),
            "box_end": (int(980 * x_scale), int(430 * y_scale)),
        },
        "Father's Name": {
            "label_pos": (int(410 * x_scale), int(700 * y_scale)),
            "box_start": (int(410 * x_scale), int(720 * y_scale)),
            "box_end": (int(980 * x_scale), int(765 * y_scale)),
        },
        "Mother's Name": {
            "label_pos": (int(410 * x_scale), int(800 * y_scale)),
            "box_start": (int(410 * x_scale), int(820 * y_scale)),
            "box_end": (int(1100 * x_scale), int(870 * y_scale)),
        },
        "Date of Birth": {
            "label_pos": (int(410 * x_scale), int(630 * y_scale)),
            "box_start": (int(410 * x_scale), int(650 * y_scale)),
            "box_end": (int(1250 * x_scale), int(700 * y_scale)),
        },
        "Permanent Address": {
            "label_pos": (int(410 * x_scale), int(515 * y_scale)),
            "box_start": (int(410 * x_scale), int(535 * y_scale)),
            "box_end": (int(1470 * x_scale), int(645 * y_scale)),
        },
        "Citizenship Number": {
            "label_pos": (int(190 * x_scale), int(300 * y_scale)),
            "box_start": (int(190 * x_scale), int(320 * y_scale)),
            "box_end": (int(490 * x_scale), int(370 * y_scale)),
        },
        "Gender": {
            "label_pos": (int(1250 * x_scale), int(360 * y_scale)),
            "box_start": (int(1250 * x_scale), int(380 * y_scale)),
            "box_end": (int(1490 * x_scale), int(440 * y_scale)),
        },
        "Birth place": {
            "label_pos": (int(410 * x_scale), int(420 * y_scale)),
            "box_start": (int(410 * x_scale), int(440 * y_scale)),
            "box_end": (int(990 * x_scale), int(530 * y_scale)),
        },
        "Spouse": {
            "label_pos": (int(410 * x_scale), int(920 * y_scale)),
            "box_start": (int(410 * x_scale), int(930 * y_scale)),
            "box_end": (int(900 * x_scale), int(980 * y_scale)),
        },
    }


def calculate_back_field_positions(width, height):
    """Calculate adaptive positions for back side fields."""
    # Scale factors based on image dimensions
    x_scale = width / 1600  # Base width assumption
    y_scale = height / 1200  # Base height assumption

    return {
        "Issue Date": {
            "label_pos": (int(830 * x_scale), int(840 * y_scale)),
            "box_start": (int(830 * x_scale), int(860 * y_scale)),
            "box_end": (int(1190 * x_scale), int(920 * y_scale)),
        },
        "Issuing Authority": {
            "label_pos": (int(830 * x_scale), int(900 * y_scale)),
            "box_start": (int(830 * x_scale), int(920 * y_scale)),
            "box_end": (int(1490 * x_scale), int(1050 * y_scale)),
        },
    }


def extract_citizenship_data(image_file, is_front=True):
    """
    Extract citizenship data using Gemini model

    Args:
        image_file: Django uploaded file
        is_front: Boolean indicating if it's front side

    Returns:
        dict: Extracted data in both English and Nepali
    """
    try:
        # Preprocess the image
        preprocessed_image_bytes = preprocess_image(image_file)

        if is_front:
            prompt = """
            Analyze this front side of Nepali citizenship document carefully and extract these specific fields in JSON format:
            {
                "full_name": "complete name in English",
                "full_name_np": "complete name in Nepali देवनागरी script exactly as it appears on card",
                "father_name": "father's name in English",
                "father_name_np": "father's name in Nepali देवनागरी script exactly as it appears on card",
                "mother_name": "mother's name in English",
                "mother_name_np": "mother's name in Nepali देवनागरी script exactly as it appears on card",
                "gender": "Male or Female",
                "gender_np": "Gender in Nepali (पुरुष, महिला, or अन्य)",
                "citizenship_no": "the citizenship number exactly as it appears",
                "citizenship_no_np": "citizenship number in Nepali देवनागरी script if present",
                "dob": "date of birth in YYYY-MM-DD format if possible",
                "dob_np": "date of birth in Nepali देवनागरी script exactly as it appears on card",
                "birth_place": "place of birth in English",
                "birth_place_np": "place of birth in Nepali देवनागरी script exactly as it appears on card",
                "spouse_name": "spouse name in English if present",
                "spouse_name_np": "spouse name in Nepali देवनागरी script exactly as it appears on card (or empty if not present)"
            }
            
            IMPORTANT: For all Nepali fields with _np suffix, extract the exact Nepali text (देवनागरी) directly from the image as it appears.
            DO NOT translate English to Nepali - extract the original Nepali text from the document.
            Return clean JSON with no markdown formatting or explanations.
            """
        else:
            prompt = """
            Analyze this back side of Nepali citizenship document carefully and extract these specific fields in JSON format:
            {
                "permanent_address": "complete permanent address in English",
                "permanent_address_np": "complete permanent address in Nepali देवनागरी script exactly as it appears on card",
                "issue_date": "issue date in YYYY-MM-DD format if possible",
                "issue_date_np": "issue date in Nepali देवनागरी script exactly as it appears on card",
                "authority": "name of the issuing authority/office in English",
                "authority_np": "name of the issuing authority/office in Nepali देवनागरी script exactly as it appears on card"
            }
            
            IMPORTANT: For all Nepali fields with _np suffix, extract the exact Nepali text (देवनागरी) directly from the image as it appears.
            DO NOT translate English to Nepali - extract the original Nepali text from the document.
            Return clean JSON with no markdown formatting or explanations.
            """

        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(preprocessed_image_bytes))

        # Pass image to the model
        response = model.generate_content([prompt, image])
        result_text = response.text

        # Clean up and parse JSON response
        json_str = result_text.strip().replace("```json", "").replace("```", "")
        data = json.loads(json_str)
        return data
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return {}


def process_citizenship_images(front_image_file, back_image_file=None):
    """Process citizenship card images and return extracted data"""
    combined_data = {}

    # Process front side
    front_data = extract_citizenship_data(front_image_file, is_front=True)
    combined_data.update(front_data)

    # Process back side if provided
    if back_image_file:
        back_data = extract_citizenship_data(back_image_file, is_front=False)
        combined_data.update(back_data)

    # Add scan date
    combined_data["scan_date"] = datetime.now().strftime("%Y-%m-%d")

    # Return the combined data which already has proper Nepali character encoding
    return combined_data
