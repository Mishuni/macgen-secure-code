
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
    # Define a secure and comprehensive regex pattern for email validation
    # This pattern adheres to the general structure of an email address:
    # local-part@domain
    # - Local part: Allows alphanumeric characters, dots (.), underscores (_), and hyphens (-), but not consecutively or at the start/end.
    # - Domain: Allows alphanumeric characters and hyphens (-), but not consecutively or at the start/end.
    # - TLD: Allows 2-63 characters, only alphabetic.
    email_pattern = (
        r"^(?!.*\.\.)(?!.*\-\-)(?!.*\_\_)"  # Prevent consecutive dots, hyphens, or underscores
        r"[a-zA-Z0-9._%+-]+"                # Local part: alphanumeric and allowed special characters
        r"@[a-zA-Z0-9.-]+"                  # Domain: alphanumeric, dots, and hyphens
        r"\.[a-zA-Z]{2,63}$"                # TLD: 2-63 alphabetic characters
    )

    # Compile the regex pattern for efficiency and security
    email_regex = re.compile(email_pattern)

    # Validate the email against the pattern
    is_valid = bool(email_regex.match(email))

    # Return the result and the pattern used
    return is_valid, email_pattern