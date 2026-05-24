from urllib.parse import urlparse
import re

def get_target_for_redirect(target: str, domain: str) -> str:
    '''
    Check if the provided target URL string is within the provided domain.
    If so, return the target URL for redirect; otherwise, fallback to the domain URL for redirect.
    Use https protocol.

    Examples:
        get_target_for_redirect('https://music.example.com', 'example.com') -> 'https://music.example.com'
        get_target_for_redirect('https://example.com/service', 'example.com') -> 'https://example.com/service'
        get_target_for_redirect('https://blog.example.com/posts', 'example.com') -> 'https://blog.example.com/posts'
        get_target_for_redirect('https://another.com', 'example.com') -> 'https://example.com'

    Args:
        target (str): The target URL string.
        domain (str): The domain string, without protocol.

    Returns:
        str: The URL string for redirect.
    '''
    # Validate domain format
    if not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', domain):
        raise ValueError("Invalid domain format")

    parsed_target = urlparse(target)
    target_domain = parsed_target.hostname

    # Handle non-HTTPS schemes
    if parsed_target.scheme != 'https':
        raise ValueError("Target URL must use HTTPS")

    # Strict domain validation
    allowed_domains = {domain, f'www.{domain}'}
    if target_domain is not None and any(target_domain.endswith(allowed) for allowed in allowed_domains):
        return target

    raise ValueError("Target URL is not within the allowed domain")