"""
Input validation and sanitization utilities for ADDY backend
"""

import re
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class ValidationError(HTTPException):
    """Custom validation error"""
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {message}"
        )


def validate_email(email: str) -> str:
    """Validate and normalize email address"""
    if not email or not isinstance(email, str):
        raise ValidationError("Email is required and must be a string")
    
    email = email.strip().lower()
    
    # Basic email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValidationError("Invalid email format")
    
    if len(email) > 254:
        raise ValidationError("Email is too long (max 254 characters)")
    
    return email


def validate_password(password: str) -> str:
    """Validate password strength"""
    if not password or not isinstance(password, str):
        raise ValidationError("Password is required and must be a string")
    
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long")
    
    if len(password) > 128:
        raise ValidationError("Password is too long (max 128 characters)")
    
    # Check for at least one letter and one number
    if not re.search(r'[a-zA-Z]', password):
        raise ValidationError("Password must contain at least one letter")
    
    if not re.search(r'[0-9]', password):
        raise ValidationError("Password must contain at least one number")
    
    return password


def validate_name(name: str, field_name: str = "Name") -> str:
    """Validate and sanitize name fields"""
    if not name or not isinstance(name, str):
        raise ValidationError(f"{field_name} is required and must be a string")
    
    name = name.strip()
    
    if len(name) < 1:
        raise ValidationError(f"{field_name} cannot be empty")
    
    if len(name) > 100:
        raise ValidationError(f"{field_name} is too long (max 100 characters)")
    
    # Allow letters, spaces, hyphens, apostrophes
    if not re.match(r"^[a-zA-Zа-яёА-ЯЁ\s\-']+$", name):
        raise ValidationError(f"{field_name} contains invalid characters")
    
    return name


def validate_age(age: Any) -> int:
    """Validate age value"""
    if age is None:
        return None
    
    try:
        age = int(age)
    except (ValueError, TypeError):
        raise ValidationError("Age must be a number")
    
    if age < 18:
        raise ValidationError("Age must be at least 18")
    
    if age > 120:
        raise ValidationError("Age must be less than 120")
    
    return age


def validate_gender(gender: Optional[str]) -> Optional[str]:
    """Validate gender field"""
    if gender is None:
        return None
    
    if not isinstance(gender, str):
        raise ValidationError("Gender must be a string")
    
    gender = gender.strip().lower()
    
    valid_genders = ['male', 'female', 'мужской', 'женский', 'other', 'другой']
    if gender not in valid_genders:
        raise ValidationError(f"Invalid gender. Must be one of: {valid_genders}")
    
    return gender


def validate_bio(bio: Optional[str]) -> Optional[str]:
    """Validate and sanitize bio text"""
    if bio is None:
        return None
    
    if not isinstance(bio, str):
        raise ValidationError("Bio must be a string")
    
    bio = bio.strip()
    
    if len(bio) > 500:
        raise ValidationError("Bio is too long (max 500 characters)")
    
    # Remove potentially dangerous HTML/script content
    bio = re.sub(r'<[^>]*>', '', bio)
    
    return bio if bio else None


def validate_url(url: Optional[str], field_name: str = "URL") -> Optional[str]:
    """Validate URL format"""
    if url is None:
        return None
    
    if not isinstance(url, str):
        raise ValidationError(f"{field_name} must be a string")
    
    url = url.strip()
    
    if not url:
        return None
    
    # Basic URL validation
    url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    if not re.match(url_pattern, url):
        raise ValidationError(f"Invalid {field_name} format")
    
    if len(url) > 500:
        raise ValidationError(f"{field_name} is too long (max 500 characters)")
    
    return url


def validate_location(location: Optional[str]) -> Optional[str]:
    """Validate location string"""
    if location is None:
        return None
    
    if not isinstance(location, str):
        raise ValidationError("Location must be a string")
    
    location = location.strip()
    
    if len(location) > 100:
        raise ValidationError("Location is too long (max 100 characters)")
    
    return location if location else None


def validate_interests(interests: Optional[str]) -> Optional[str]:
    """Validate interests string"""
    if interests is None:
        return None
    
    if not isinstance(interests, str):
        raise ValidationError("Interests must be a string")
    
    interests = interests.strip()
    
    if len(interests) > 300:
        raise ValidationError("Interests are too long (max 300 characters)")
    
    return interests if interests else None


def sanitize_input_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize dictionary input by removing None values and trimming strings"""
    sanitized = {}
    
    for key, value in data.items():
        if value is None:
            continue
        
        if isinstance(value, str):
            value = value.strip()
            if not value:
                continue
        
        sanitized[key] = value
    
    return sanitized


def validate_personality_data(personality_data: Any) -> Dict[str, Any]:
    """Validate personality data structure"""
    if not isinstance(personality_data, dict):
        raise ValidationError("Personality data must be a dictionary")
    
    # Check for required keys
    if not personality_data:
        raise ValidationError("Personality data cannot be empty")
    
    # Validate specific fields if they exist
    if 'communication_style' in personality_data:
        style = personality_data['communication_style']
        if not isinstance(style, str) or len(style) > 50:
            raise ValidationError("Communication style must be a string (max 50 characters)")
    
    if 'interests' in personality_data:
        interests = personality_data['interests']
        if isinstance(interests, list):
            if len(interests) > 20:
                raise ValidationError("Too many interests (max 20)")
            for interest in interests:
                if not isinstance(interest, str) or len(interest) > 50:
                    raise ValidationError("Each interest must be a string (max 50 characters)")
    
    return personality_data