
from typing import Dict
import re

def is_valid_lang(lang: str) -> bool:
    # A regex to validate language codes (e.g., 'en', 'fr', 'en-US')
    return bool(re.match(r'^[a-z]{2}(-[A-Z]{2})?$', lang))

def is_valid_encoding(encoding: str) -> bool:
    # A check for common encoding types
    valid_encodings = {'gzip', 'deflate', 'br', 'identity', 'compress'}
    return encoding in valid_encodings

def is_valid_cache(cache: str) -> bool:
    # A check for valid cache control directives
    valid_cache_directives = {
        'no-cache', 'no-store', 'must-revalidate', 
        'max-age', 'public', 'private', 
        'max-age=0', 's-maxage', 'immutable'
    }
    # Split cache directives and check if all are valid
    directives = [directive.strip() for directive in cache.split(',')]
    return all(directive in valid_cache_directives for directive in directives)

def sanitize_input(input_str: str) -> str:
    # Sanitize input to prevent header injection attacks
    return re.sub(r'[^\w-,:=]', '', input_str)  # Allow only word characters, hyphens, commas, colons, and equal signs

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
    sanitized_content = sanitize_input(info_content)

    if info_type == 'lang' and is_valid_lang(sanitized_content):
        header['Accept-Language'] = sanitized_content
    elif info_type == 'encoding' and is_valid_encoding(sanitized_content):
        header['Accept-Encoding'] = sanitized_content
    elif info_type == 'cache' and is_valid_cache(sanitized_content):
        header['Cache-Control'] = sanitized_content
    else:
        return header  # Return the original header if the info_type is invalid or content is not valid

    return header  # Return the updated header