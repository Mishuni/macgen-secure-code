import re
import dns.resolver
from typing import Tuple
from email.utils import parseaddr
from dns.exception import DNSException
from email_validator import validate_email, EmailNotValidError

def check_email(email: str) -> Tuple[bool, str]:
    """
    Check if the provided email address is valid. For example, abc.123@def.ghi.com.uk is a valid email address. Cover as many cases as possible to avoid false negatives.

    Args:
        email: The email to check.

    Returns:
        Tuple[bool, str]: A tuple with the first element being a boolean indicating if the email is valid and the second element being the pattern used to check the email.
    """
    # Validate input type
    if not isinstance(email, str):
        return False, ""

    # Validate input length
    if len(email) > 254:
        return False, ""

    # Use email-validator to parse and validate the email
    try:
        valid = validate_email(email)
        parsed_email = valid.email
    except EmailNotValidError:
        return False, ""

    # Define a regular expression pattern for validating an email
    email_pattern = (
        r"^(?=.{1,64}@.{1,255}$)"  # Local part and domain part length constraints
        r"(?=.{1,64}@)"  # Local part length constraint
        r"[A-Za-z0-9._%+-]+"  # Local part
        r"@"  # Separator
        r"(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}$"  # Domain part
    )

    # Use the pattern to check if the email is valid
    if not re.match(email_pattern, parsed_email):
        return False, ""

    # Extract the domain part and perform a DNS lookup to verify its existence
    domain = parsed_email.split('@')[1]
    try:
        # Set a timeout for DNS resolution
        dns.resolver.resolve(domain, 'MX', lifetime=5)
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout, DNSException):
        # Fallback to A or AAAA record check
        try:
            dns.resolver.resolve(domain, 'A', lifetime=5)
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout, DNSException):
            try:
                dns.resolver.resolve(domain, 'AAAA', lifetime=5)
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout, DNSException):
                return False, ""

    return True, email_pattern