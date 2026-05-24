import re

def get_url_to_visit(domain: str, subdomain_prefix: str) -> str:
    # Define a list of trusted domains
    trusted_domains = {'example.com', 'trusted.com', 'secure.org'}
    
    # Validate the domain against the trusted list
    if domain not in trusted_domains:
        raise ValueError("Domain is not trusted.")
    
    # Define a regex pattern for valid subdomain
    subdomain_pattern = re.compile(r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})*$')
    
    # Check if the subdomain_prefix is valid
    if subdomain_prefix and subdomain_pattern.match(subdomain_prefix):
        return f"https://{subdomain_prefix}.{domain}"
    else:
        return f"https://{domain}"