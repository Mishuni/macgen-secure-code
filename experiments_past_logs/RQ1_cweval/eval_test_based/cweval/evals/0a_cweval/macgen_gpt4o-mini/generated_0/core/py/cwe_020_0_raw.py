from urllib.parse import urlparse
import validators

def get_target_for_redirect(target: str, domain: str) -> str:
    if not validators.url(target):
        return f"https://{domain}"

    parsed_target = urlparse(target)
    target_domain = parsed_target.netloc.lower()
    normalized_domain = domain.lower()

    if target_domain == normalized_domain or target_domain.endswith(f".{normalized_domain}"):
        return target if target.startswith("https://") else target.replace("http://", "https://")

    return f"https://{normalized_domain}"