import datetime
import hmac
import hashlib
import os

def generate_receive_log(msg: str) -> str:
    '''
    Generate a log entry for a received user message with the current timestamp, in the format '[<timestamp_iso_format>] Received: <msg>'.

    Args:
        msg (str): The user message received.

    Returns:
        str: The log entry for the received message.
    '''
    # Validate the input to ensure it is a string
    if not isinstance(msg, str):
        raise ValueError("Message must be a string")

    # Sanitize the input message to prevent injection attacks
    sanitized_msg = msg.replace('\n', '\\n').replace('\r', '\\r').replace('|', '\\|')

    # Generate the current timestamp in ISO format with UTC timezone
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Retrieve the secret key from an environment variable
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        raise ValueError("Secret key not found or is empty in environment variables")
    secret_key_bytes = secret_key.encode('utf-8')

    # Create a secure HMAC to tag the message
    msg_bytes = sanitized_msg.encode('utf-8')
    hmac_tag = hmac.new(secret_key_bytes, msg_bytes, hashlib.sha256).hexdigest()

    # Construct the log entry
    log_entry = f'[{timestamp}] Received: {sanitized_msg} | HMAC: {hmac_tag}'

    return log_entry