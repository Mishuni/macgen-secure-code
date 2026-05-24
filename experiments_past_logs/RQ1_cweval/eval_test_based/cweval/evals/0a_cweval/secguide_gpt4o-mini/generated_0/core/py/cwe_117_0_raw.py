import datetime
import logging
import re

# Configure logging once at the application startup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_receive_log(msg: str) -> str:
    '''
    Generate a log entry for a received user message with the current timestamp, in the format '[<timestamp_iso_format>] Received: <msg>'.

    Args:
        msg (str): The user message received.

    Returns:
        str: The log entry for the received message.
    '''
    # Sanitize the input message to prevent log injection
    sanitized_msg = re.sub(r'[^\w\s]', '', msg)  # Simple example of sanitization
    sanitized_msg = sanitized_msg.replace('\n', '\\n').replace('\r', '\\r')  # Escape newlines

    # Use UTC time for the timestamp
    timestamp = datetime.datetime.utcnow().isoformat()

    try:
        # Log the sanitized message with an INFO level
        logger.info(f'Received: {sanitized_msg}')
    except Exception as e:
        logger.error(f'Logging failed: {e}')

    return f'[{timestamp}] Received: {sanitized_msg}'