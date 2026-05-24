
import datetime
import html

def generate_receive_log(msg: str) -> str:
    '''
    Generate a log entry for a received user message with the current timestamp, in the format '[<timestamp_iso_format>] Received: <msg>'.

    Args:
        msg (str): The user message received.

    Returns:
        str: The log entry for the received message.
    '''
    try:
        # Get the current timestamp in ISO 8601 format
        timestamp = datetime.datetime.now().isoformat()

        # Sanitize and escape the user-provided message to prevent injection attacks
        sanitized_msg = html.escape(msg)

        # Construct the log entry
        log_entry = f"[{timestamp}] Received: {sanitized_msg}"

        return log_entry
    except Exception as e:
        # Log the error securely and return a generic error message
        # Note: In a real-world scenario, you would log the error to a secure logging system
        return "[Error] Unable to generate log entry"