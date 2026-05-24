
from typing import Dict
from html import escape

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
    valid_info_types = {
        'lang': 'Accept-Language',
        'encoding': 'Accept-Encoding',
        'cache': 'Cache-Control'
    }

    try:
        # Validate the info_type
        if info_type not in valid_info_types:
            return header  # Return the original header if the info_type is invalid

        # Escape the info_content to prevent injection attacks
        safe_info_content = escape(info_content)

        # Update the header with the sanitized content
        header[valid_info_types[info_type]] = safe_info_content

        return header  # Return the updated header
    except Exception:
        # Gracefully handle any unexpected errors and return the original header
        return header