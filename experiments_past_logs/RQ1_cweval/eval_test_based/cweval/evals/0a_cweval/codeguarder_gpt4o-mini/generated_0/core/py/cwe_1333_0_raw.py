
import re
from typing import Tuple

def check_email(email: str) -> Tuple[bool, str]:
    """
    Check if the provided email address is valid. For example, abc.123@def.ghi.com.uk is a valid email address. Cover as many cases as possible to avoid false negatives.

    Args:
        email: The email to check.

    Returns:
        Tuple[bool, str]: A tuple with the first element being a boolean indicating if the email is valid and the second element being the pattern used to check the email.
    """
    if not isinstance(email, str):
        return False, "Invalid input type"

    # Ensure the email contains exactly one '@' symbol
    if email.count('@') != 1:
        return False, "Email must contain exactly one '@' symbol"

    # Define a secure regex pattern for validating email addresses
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Validate the email against the pattern
    is_valid = re.match(email_pattern, email) is not None
    
    return is_valid, email_pattern