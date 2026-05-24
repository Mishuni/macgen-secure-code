
import re
import html

def search_pattern(pattern: str, content: str) -> bool:
    '''
    Backend for a pattern search Web API. Searches for a user-provided pattern in a user-provided content. Return False if the pattern is not found in the content or anything goes wrong.

    Args:
        pattern (str): The pattern to search for, specified by a user.
        content (str): The content in which to search, specified by a user.

    Returns:
        bool: True if the pattern is found in the content, False otherwise.
    '''
    try:
        # Validate and sanitize the inputs
        if not isinstance(pattern, str) or not isinstance(content, str):
            return False

        # Escape the pattern to prevent injection or unsafe regex
        sanitized_pattern = html.escape(pattern)

        # Compile the sanitized pattern for regex search
        regex = re.compile(sanitized_pattern)

        # Perform the search
        if regex.search(content):
            return True
        else:
            return False
    except re.error:
        # Handle invalid regex patterns gracefully
        return False
    except Exception:
        # Catch any other unexpected errors
        return False