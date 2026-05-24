from urllib.parse import urlparse, urlunparse
import re
import idna
from publicsuffix2 import get_sld

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
    # Define a stricter regex pattern for valid subdomain
    subdomain_pattern = re.compile(r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63}){0,2}$')

    # Validate the subdomain prefix
    if subdomain_prefix and subdomain_pattern.match(subdomain_prefix):
        # Encode the subdomain using IDNA to handle internationalized domain names
        try:
            subdomain_prefix = idna.encode(subdomain_prefix).decode('ascii')
            netloc = f"{subdomain_prefix}.{domain}"
        except idna.IDNAError:
            netloc = domain
    else:
        netloc = domain

    # Construct the URL using urlunparse for safety
    url = urlunparse(('https', netloc, '', '', '', ''))
    
    # Parse the URL to ensure it is correctly formed
    try:
        parsed_url = urlparse(url)
        # Ensure the netloc ends with the trusted domain using publicsuffix2
        if get_sld(parsed_url.netloc) != domain:
            return urlunparse(('https', domain, '', '', '', ''))
    except ValueError:
        return urlunparse(('https', domain, '', '', '', ''))
    
    # Return the constructed URL
    return parsed_url.geturl()