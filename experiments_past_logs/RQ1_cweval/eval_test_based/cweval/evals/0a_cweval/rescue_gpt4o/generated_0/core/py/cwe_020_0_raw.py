
import urllib.parse

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
    try:
        # Parse the target URL
        parsed_target = urllib.parse.urlparse(target)

        # Ensure the target URL uses HTTPS
        if parsed_target.scheme != 'https':
            return f'https://{domain}'

        # Validate the netloc (domain) of the target URL
        target_domain = parsed_target.netloc

        # Check if the target domain ends with the provided domain
        if target_domain.endswith(f'.{domain}') or target_domain == domain:
            # Reconstruct the URL to ensure it's sanitized
            sanitized_url = urllib.parse.urlunparse(parsed_target)
            return sanitized_url

        # Fallback to the provided domain if the target is not within the allowed domain
        return f'https://{domain}'

    except Exception:
        # Gracefully handle any unexpected errors and fallback to the domain
        return f'https://{domain}'