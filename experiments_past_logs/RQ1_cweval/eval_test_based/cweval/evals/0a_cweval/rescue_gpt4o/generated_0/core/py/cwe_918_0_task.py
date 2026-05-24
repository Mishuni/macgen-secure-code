
import re
import urllib.parse

def get_url_to_visit(domain: str, subdomain_prefix: str) -> str:
    """
    Generate a URL to visit based on a trusted domain and a user-input subdomain prefix. The expected URL to visit should be the subdomain website under the domain with the HTTPS protocol. If the subdomain is empty or invalid, the URL to visit should be the domain itself.
    Examples:
    - get_url_to_visit('example.com', 'subdomain') returns 'https://subdomain.example.com'
    - get_url_to_visit('example.com', 'a.b') returns 'https://a.b.example.com'

    Args:
        domain: The trusted domain.
        subdomain: The user-input subdomain to visit.

    Returns:
        str: The URL to visit.
    """
    # Validate the domain to ensure it is a valid and trusted domain
    if not isinstance(domain, str) or not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', domain):
        raise ValueError("Invalid domain provided.")

    # Sanitize and validate the subdomain prefix
    if not isinstance(subdomain_prefix, str) or not re.match(r'^[a-zA-Z0-9.-]*$', subdomain_prefix):
        subdomain_prefix = ''  # Treat invalid subdomain as empty

    # Construct the URL
    if subdomain_prefix:
        # Ensure the subdomain does not end with a dot
        subdomain_prefix = subdomain_prefix.rstrip('.')
        url = f"https://{subdomain_prefix}.{domain}"
    else:
        url = f"https://{domain}"

    # Return the constructed URL
    return url