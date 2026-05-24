from typing import Dict
import re
import unicodedata

def store_info_in_header(
    info_type: str, info_content: str, header: Dict[str, str]
) -> Dict[str, str]:
    valid_info_types = {
        'lang': 'Accept-Language',
        'encoding': 'Accept-Encoding',
        'cache': 'Cache-Control'
    }
    
    # Normalize and validate info_content
    info_content = unicodedata.normalize("NFC", info_content)
    if not re.match(r'^[a-zA-Z0-9,;._\- ]*$', info_content):
        return header  # Return original header if validation fails

    if info_type in valid_info_types:
        header_key = valid_info_types[info_type]
        try:
            header[header_key] = info_content
        except Exception:
            return header  # Return original header on error
    
    return header