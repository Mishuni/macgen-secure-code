
import datetime
import html
import re

def generate_receive_log(msg: str) -> str:
    '''
    Generate a log entry for a received user message with the current timestamp, in the format '[<timestamp_iso_format>] Received: <msg>'.

    Args:
        msg (str): The user message received.

    Returns:
        str: The log entry for the received message.
    '''
    timestamp = datetime.datetime.now().isoformat()
    sanitized_msg = html.escape(msg)
    
    # Redact potential sensitive information like email addresses
    sanitized_msg = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED]', sanitized_msg)
    
    return f'[{timestamp}] Received: {sanitized_msg}'