from typing import Dict
import re

MAX_INFO_CONTENT_LENGTH = 100

def store_info_in_header(
    info_type: str, info_content: str, header: Dict[str, str]
) -> Dict[str, str]:
    valid_types = {
        'lang': 'Accept-Language',
        'encoding': 'Accept-Encoding',
        'cache': 'Cache-Control'
    }
    
    if info_type not in valid_types:
        return header
    
    # Sanitize info_content to remove newline and control characters
    info_content = re.sub(r'[\r\n]', '', info_content)
    info_content = ''.join(c for c in info_content if c.isprintable())
    
    if len(info_content) > MAX_INFO_CONTENT_LENGTH:
        return header
    
    header[valid_types[info_type]] = info_content
    return header