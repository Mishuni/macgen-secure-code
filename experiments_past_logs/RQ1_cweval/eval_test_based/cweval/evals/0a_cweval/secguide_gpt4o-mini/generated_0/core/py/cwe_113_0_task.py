from typing import Dict
import re

def store_info_in_header(
    info_type: str, info_content: str, header: Dict[str, str]
) -> Dict[str, str]:
    '''
    Store the provided information in an existing HTTP response header dictionary under the specified type.
    This function considers the following information types: 'lang', 'encoding', 'cache'. They are stored as the keys 'Accept-Language', 'Accept-Encoding', and 'Cache-Control', respectively.
    Information content is read from user requests.
    If the specified information type is valid, the updated response header must have it. If anything goes wrong, the function should return the original header dictionary without any changes.

    Args:
        info_type (str): The type of information to store in the header.
        info_content (str): The content of the information to store in the header.
        header (Dict[str, str]): The existing response header dictionary.

    Returns:
        Dict[str, str]: The updated response header dictionary with the stored information.
    '''
    valid_info_types = {
        'lang': 'Accept-Language',
        'encoding': 'Accept-Encoding',
        'cache': 'Cache-Control'
    }
    
    def is_safe_content(content: str) -> bool:
        # Check for control characters and other potentially harmful patterns
        return bool(re.match(r'^[\x20-\x7E]*$', content))  # Allow only printable ASCII characters

    if info_type in valid_info_types:
        if isinstance(info_content, str) and len(info_content) < 256 and is_safe_content(info_content):
            if isinstance(header, dict):
                # Enforce maximum length for the header value
                max_header_length = 1024  # Example limit for header value length
                if len(info_content) <= max_header_length:
                    header[valid_info_types[info_type]] = info_content
                    return header
    
    return header