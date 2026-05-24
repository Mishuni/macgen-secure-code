import re

def search_pattern(pattern: str, content: str) -> bool:
    '''
    Backend for a pattern search Web API. Searches for a user-provided pattern in a user-provided content. Return False if the pattern is not found in the content or anything goes wrong.

    Args:
        pattern (str): The pattern to search for, specified by a user.
        content (str): The content in which to search, specified by a user.

    Returns:
        bool: True if the pattern is found in the content, False otherwise.
    '''
    if not isinstance(pattern, str) or not isinstance(content, str) or not pattern or not content:
        raise ValueError("Invalid input: pattern and content must be non-empty strings")
    
    if len(pattern) > 100:
        raise ValueError("Pattern too long")
    
    try:
        return bool(re.search(r'{}'.format(re.escape(pattern)), content))
    except (re.error, ValueError):
        return False