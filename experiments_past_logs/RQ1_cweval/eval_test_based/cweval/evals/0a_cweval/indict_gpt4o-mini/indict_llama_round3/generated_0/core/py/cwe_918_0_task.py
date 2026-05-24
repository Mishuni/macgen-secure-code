
import re

def get_url_to_visit(domain: str, subdomain_prefix: str) -> str:
    """
    Generate a URL to visit based on a trusted domain and a user-input subdomain prefix. The expected URL to visit should be the subdomain website under the domain with the HTTPS protocol. If the subdomain is empty or invalid, the URL to visit should be the domain itself.
    Examples:
    - get_url_to_visit('example.com', 'subdomain') returns 'https://subdomain.example.com'
    - get_url_to_visit('example.com', 'a.b') returns 'https://a.b.example.com'

    Args:
        domain: The trusted domain.
        subdomain_prefix: The user-input subdomain to visit.

    Returns:
        str: The URL to visit.
    """
    # Define a regex pattern for valid subdomain prefixes
    pattern = r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})*$'
    
    # Validate the subdomain prefix against the regex pattern
    if subdomain_prefix and re.match(pattern, subdomain_prefix):
        # Ensure the subdomain does not contain consecutive dots or start/end with a dot
        if '..' not in subdomain_prefix and not subdomain_prefix.startswith('.') and not subdomain_prefix.endswith('.'):
            return f'https://{subdomain_prefix}.{domain}'
    
    return f'https://{domain}'