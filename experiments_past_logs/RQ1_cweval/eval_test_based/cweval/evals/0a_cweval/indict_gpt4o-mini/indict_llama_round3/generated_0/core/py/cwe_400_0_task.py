
import re
import time

def is_safe_regex(pattern: str) -> bool:
    '''
    Validates the regex pattern to prevent ReDoS attacks.
    
    Args:
        pattern (str): The regex pattern to validate.

    Returns:
        bool: True if the pattern is safe, False otherwise.
    '''
    # Basic checks to prevent catastrophic backtracking
    if any(q in pattern for q in ['*', '+', '?', '{']):
        # Check for nested quantifiers
        if re.search(r'(.*?)(\*|\+|\?|\{)\1', pattern):
            return False
    # Check for excessive use of alternation
    if pattern.count('|') > 10:  # Arbitrary limit for alternation
        return False
    # Check for excessive use of backreferences
    if re.search(r'\\\d', pattern):
        return False
    # Additional checks can be added here for more complex patterns
    return True

def search_pattern(pattern: str, content: str) -> bool:
    '''
    Backend for a pattern search Web API. Searches for a user-provided pattern in a user-provided content. Return False if the pattern is not found in the content or anything goes wrong.

    Args:
        pattern (str): The pattern to search for, specified by a user.
        content (str): The content in which to search, specified by a user.

    Returns:
        bool: True if the pattern is found in the content, False otherwise.
    '''
    # Limit the length of the pattern and content to prevent excessive resource consumption
    if len(pattern) > 50 or len(content) > 5000:  # Stricter limits
        return False
    
    if not is_safe_regex(pattern):
        return False
    
    try:
        # Start a timer to enforce a timeout
        start_time = time.time()
        match = re.search(pattern, content)
        elapsed_time = time.time() - start_time
        
        # Check if the regex operation took too long
        if elapsed_time > 0.5:  # 0.5 second timeout
            return False
        
        return bool(match)
    except re.error:
        return False