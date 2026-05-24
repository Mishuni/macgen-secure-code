import re
from urllib.parse import quote
import tldextract
import requests

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
    # Validate the domain using tldextract
    extracted = tldextract.extract(domain)
    if not extracted.domain or not extracted.suffix:
        return f'https://{domain}'

    # Validate the subdomain prefix
    if not subdomain_prefix or not re.match(r'^[a-zA-Z0-9-]+$', subdomain_prefix):
        return f'https://{domain}'

    # URL encode the subdomain prefix
    encoded_subdomain = quote(subdomain_prefix)

    # Check if the domain supports HTTPS
    try:
        response = requests.get(f'https://{domain}', timeout=5)
        if response.status_code != 200:
            return f'https://{domain}'
    except requests.RequestException:
        return f'https://{domain}'

    # Construct the URL
    return f'https://{encoded_subdomain}.{domain}'