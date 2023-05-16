import re

def validate_password(password):
    """Validate password based on given requirements."""
    # Check length
    if len(password) < 40:
        print("Password must be at least 40 characters long.")
        return False

    # Check for lowercase, uppercase, and numeric characters
    if not re.search(r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)", password):
        print("Password must contain at least one lowercase letter, one uppercase letter, and one number.")
        return False

    return True

def is_valid_email(email):
    """
    Validates if a given text is a valid email address or not.

    Args:
    email (str): The email address to be validated.

    Returns:
    bool: True if the email address is valid, False otherwise.
    """
    # Regular expression pattern to validate email addresses
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    # Use regular expression to match the pattern
    if re.match(pattern, email):
        return True
    else:
        return False
