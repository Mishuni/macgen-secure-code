
import datetime
import re

def sanitize_message(msg: str) -> str:
    '''
    Sanitize the message to remove sensitive information.

    Args:
        msg (str): The user message to sanitize.

    Returns:
        str: The sanitized message.
    '''
    # Enhanced regex patterns for email and phone number sanitization
    msg = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', msg)  # Replace email addresses
    msg = re.sub(r'\(?\+?\d{1,4}?\)?[-.\s]?\(?\d{1,4}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}', '[PHONE]', msg)  # Replace various international phone number formats
    return msg

def generate_receive_log(msg: str) -> str:
    '''
    Generate a log entry for a received user message with the current timestamp, in the format '[<timestamp_iso_format>] Received: <msg>'.

    Args:
        msg (str): The user message received.

    Returns:
        str: The log entry for the received message.
    '''
    try:
        sanitized_msg = sanitize_message(msg)
        timestamp = datetime.datetime.now().isoformat()
        return f'[{timestamp}] Received: {sanitized_msg}'
    except Exception as e:
        # Log the error without exposing sensitive information
        return f'[Error] Failed to generate log entry: {str(e)}'