from urllib.parse import urlparse

def get_target_for_redirect(target: str, domain: str) -> str:
    try:
        parsed_url = urlparse(target)
        if parsed_url.scheme and parsed_url.hostname:
            target_domain = parsed_url.hostname
            if target_domain.lower().endswith(domain.lower()):
                return target
        return f'https://{domain}'
    except Exception:
        return f'https://{domain}'