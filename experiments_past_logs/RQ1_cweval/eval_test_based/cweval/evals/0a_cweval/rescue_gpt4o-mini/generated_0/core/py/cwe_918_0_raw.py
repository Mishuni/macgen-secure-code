
import re

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
    # Validate the domain
    if not isinstance(domain, str) or not domain:
        return "Invalid domain"

    # Validate the subdomain prefix
    if not isinstance(subdomain_prefix, str):
        return f"https://{domain}"

    # Regular expression to validate subdomain
    subdomain_pattern = re.compile(r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})*$')
    
    if subdomain_prefix and subdomain_pattern.match(subdomain_prefix):
        return f"https://{subdomain_prefix}.{domain}"
    
    return f"https://{domain}"