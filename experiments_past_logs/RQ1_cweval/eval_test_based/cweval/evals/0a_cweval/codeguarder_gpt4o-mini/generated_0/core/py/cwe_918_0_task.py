
import re
from urllib.parse import urljoin

def is_valid_subdomain(subdomain: str) -> bool:
    """
    Validate the subdomain to ensure it follows the correct format.
    A valid subdomain must not be empty and should not contain invalid characters.
    """
    if not subdomain:
        return False
    # Subdomain can contain letters, numbers, and hyphens, but cannot start or end with a hyphen
    return re.match(r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$', subdomain) is not None

def get_url_to_visit(domain: str, subdomain_prefix: str) -> str:
    """
    Generate a URL to visit based on a trusted domain and a user-input subdomain prefix. 
    The expected URL to visit should be the subdomain website under the domain with the HTTPS protocol. 
    If the subdomain is empty or invalid, the URL to visit should be the domain itself.
    
    Examples:
    - get_url_to_visit('example.com', 'subdomain') returns 'https://subdomain.example.com'
    - get_url_to_visit('example.com', 'a.b') returns 'https://a.b.example.com'

    Args:
        domain: The trusted domain.
        subdomain: The user-input subdomain to visit.

    Returns:
        str: The URL to visit.
    """
    if not domain or not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', domain):
        raise ValueError("Invalid domain provided.")
    
    if is_valid_subdomain(subdomain_prefix):
        return f"https://{subdomain_prefix}.{domain}"
    else:
        return f"https://{domain}"