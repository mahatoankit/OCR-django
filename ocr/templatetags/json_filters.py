from django import template
import json
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="pretty_json")
def pretty_json(value):
    """
    Template filter that properly renders JSON with Unicode characters
    """
    try:
        if not value:
            return ""
        # First parse the JSON if it's a string
        if isinstance(value, str):
            data = json.loads(value)
        else:
            data = value
        # Re-serialize with ensure_ascii=False to preserve Unicode characters
        formatted_json = json.dumps(data, indent=2, ensure_ascii=False)
        # Mark the output as safe to prevent HTML escaping
        return mark_safe(formatted_json)
    except Exception as e:
        return f"Error formatting JSON: {str(e)}"


@register.filter(name="get_json_value")
def get_json_value(json_string, key):
    """
    Template filter to get a specific value from a JSON string
    """
    try:
        if not json_string:
            return ""
        # Parse the JSON if it's a string
        if isinstance(json_string, str):
            data = json.loads(json_string)
        else:
            data = json_string
        # Return the value for the given key, or empty string if key doesn't exist
        return data.get(key, "")
    except Exception as e:
        return f"Error extracting JSON value for key '{key}': {str(e)}"


@register.simple_tag
def get_json_field(json_string, field_name, default="Not detected"):
    """A simple tag to get a value from JSON with a default"""
    try:
        if json_string is None or json_string == "":
            return default

        # Parse the JSON if it's a string
        if isinstance(json_string, str):
            try:
                json_string = json_string.strip()
                data = json.loads(json_string)
            except json.JSONDecodeError:
                return f"[JSON Error: Invalid format]"
        else:
            data = json_string

        # Check if data is a dictionary
        if not isinstance(data, dict):
            return f"[Error: Not a dictionary]"

        # Get the value from the data
        value = data.get(field_name)
        if value is None or value == "":
            return default
        return value
    except Exception as e:
        return f"[Error: {str(e)}]"


@register.filter(name="type_of")
def type_of(value):
    return type(value).__name__


@register.filter(name="format_json")
def format_json(value):
    """Format JSON string with proper Nepali character display"""
    try:
        if not value:
            return ""
        data = json.loads(value)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except:
        return value
