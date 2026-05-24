
from urllib.parse import urlparse

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
    parsed_target = urlparse(target)

    # Ensure the target URL uses HTTPS
    if parsed_target.scheme != 'https':
        return f'https://{domain}'

    target_domain = parsed_target.netloc

    # Normalize the domain for comparison
    if target_domain.startswith('www.'):
        target_domain = target_domain[4:]

    # Check if the target domain is valid and matches the provided domain
    if target_domain == domain or target_domain.endswith(f'.{domain}'):
        return target

    # Fallback to the domain URL with https protocol
    return f'https://{domain}'