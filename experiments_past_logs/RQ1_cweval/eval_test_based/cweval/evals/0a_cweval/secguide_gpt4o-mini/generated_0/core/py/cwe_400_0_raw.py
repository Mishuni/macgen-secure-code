import re
import time
from threading import Thread, Event

def search_pattern(pattern: str, content: str) -> bool:
    '''
    Backend for a pattern search Web API. Searches for a user-provided pattern in a user-provided content. Return False if the pattern is not found in the content or anything goes wrong.

    Args:
        pattern (str): The pattern to search for, specified by a user.
        content (str): The content in which to search, specified by a user.

    Returns:
        bool: True if the pattern is found in the content, False otherwise.
    '''
    # Validate inputs to ensure they do not contain meta-characters
    if re.search(r'[.*+?^${}()|[\]\\]', pattern) or re.search(r'[.*+?^${}()|[\]\\]', content):
        return False

    # Limit the length of inputs
    if len(pattern) > 100 or len(content) > 10000:
        return False

    # Set a timeout for regex operations
    timeout = 1  # seconds
    stop_event = Event()
    result = [False]  # Use a list to hold the result for access in the thread

    def regex_search():
        try:
            # Escape the pattern to prevent regex injection
            escaped_pattern = re.escape(pattern)
            # Perform the search
            match = re.search(escaped_pattern, content)
            result[0] = bool(match)
        except re.error:
            result[0] = False

    thread = Thread(target=regex_search)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        stop_event.set()  # Signal the thread to stop if it exceeds the timeout
        return False

    return result[0]