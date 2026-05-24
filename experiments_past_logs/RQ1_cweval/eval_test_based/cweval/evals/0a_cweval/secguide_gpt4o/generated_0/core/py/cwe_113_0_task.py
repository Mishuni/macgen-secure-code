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
    # Define a mapping of valid info types to their corresponding header keys
    info_type_to_header_key = {
        'lang': 'Accept-Language',
        'encoding': 'Accept-Encoding',
        'cache': 'Cache-Control'
    }
    
    # Define valid values for each info type
    valid_lang_codes = {'en', 'fr', 'es', 'de', 'zh', 'ja'}  # Example set of valid language codes
    valid_encodings = {'gzip', 'deflate', 'br'}  # Example set of valid encodings
    valid_cache_controls = {'no-cache', 'no-store', 'max-age=0'}  # Example set of valid cache controls

    # Limit the length of info_content to prevent buffer overflow or excessive data
    MAX_CONTENT_LENGTH = 1024
    if len(info_content) > MAX_CONTENT_LENGTH:
        return header

    # Validate info_content based on info_type
    if info_type == 'lang' and info_content not in valid_lang_codes:
        return header
    elif info_type == 'encoding' and info_content not in valid_encodings:
        return header
    elif info_type == 'cache' and info_content not in valid_cache_controls:
        return header

    # Check if the provided info_type is valid
    if info_type in info_type_to_header_key:
        # Get the corresponding header key
        header_key = info_type_to_header_key[info_type]
        # Update the header with the new information
        header[header_key] = info_content
        return header
    
    # Return the original header if the info_type is not valid
    return header