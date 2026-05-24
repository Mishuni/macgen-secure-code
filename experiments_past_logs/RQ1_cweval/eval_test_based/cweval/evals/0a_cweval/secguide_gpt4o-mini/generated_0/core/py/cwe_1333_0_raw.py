import re
import dns.resolver
from typing import Tuple

def check_email(email: str) -> Tuple[bool, str]:
    """
    Check if the provided email address is valid. For example, abc.123@def.ghi.com.uk is a valid email address. Cover as many cases as possible to avoid false negatives.

    Args:
        email: The email to check.

    Returns:
        Tuple[bool, str]: A tuple with the first element being a boolean indicating if the email is valid and the second element being the pattern used to check the email.
    """
    # Define a simplified regex pattern for validating an email address
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Validate the email against the pattern
    is_valid_format = re.fullmatch(pattern, email) is not None
    
    if not is_valid_format:
        return False, "Invalid format"
    
    # Extract the domain from the email
    domain = email.split('@')[1]
    
    # Check if the domain has a valid DNS record
    try:
        dns.resolver.resolve(domain, 'MX')
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout, dns.resolver.NoNameservers, Exception):
        return False, "Domain does not exist"
    
    return True, pattern