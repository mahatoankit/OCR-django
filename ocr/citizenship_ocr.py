import google.generativeai as genai
from PIL import Image
import io
import json
import cv2
import numpy as np
from datetime import datetime

# Configure Gemini API
genai.configure(api_key="AIzaSyCotnndBVRVBcGlHUiKbP_I_mTmAr1Ages")
model = genai.GenerativeModel("gemini-2.0-flash")

def preprocess_image(image_file):
    """Preprocess image for better OCR results"""
    # Read the image
    img_bytes = image_file.read()
    image_file.seek(0)  # Reset file pointer
    
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

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

def extract_citizenship_data(image_file, is_front=True):
    """
    Extract citizenship data using Gemini model
    
    Args:
        image_file: Django uploaded file
        is_front: Boolean indicating if it's front side
        
    Returns:
        dict: Extracted data
    """
    # Preprocess the image
    preprocessed_image_bytes = preprocess_image(image_file)
    
    if is_front:
        prompt = """
        Analyze this front side of Nepali citizenship document carefully and extract these specific fields in JSON format:
        {
            "full_name": "complete name in English",
            "father_name": "father's name in English",
            "mother_name": "mother's name in English",
            "gender": "Male or Female",
            "citizenship_no": "the citizenship number exactly as it appears",
            "dob": "date of birth in YYYY-MM-DD format if possible",
            "birth_place": "place of birth in English",
            "issue_date": "issue date in YYYY-MM-DD format if possible",
            "authority": "name of the issuing authority/office"
        }
        
        Look carefully for Nepali text (देवनागरी) and translate to English when needed.
        Focus only on extracting these fields - no additional information.
        Return clean JSON with no markdown formatting or explanations.
        """
    else:
        prompt = """
        Analyze this back side of Nepali citizenship document carefully and extract these specific fields in JSON format:
        {
            "permanent_address": "complete permanent address in English",
            "spouse_name": "spouse's name in English if present"
        }
        
        Look carefully for Nepali text (देवनागरी) and translate to English when needed.
        Focus only on extracting these fields - no additional information.
        Return clean JSON with no markdown formatting or explanations.
        """
    
    try:
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

def process_citizenship_image(image_file):
    """Process a citizenship image and extract data"""
    # Assume it's a front side image since we're handling one image at a time
    data = extract_citizenship_data(image_file, is_front=True)
    
    # Add scan date
    data["scan_date"] = datetime.now().strftime("%Y-%m-%d")
    
    return data