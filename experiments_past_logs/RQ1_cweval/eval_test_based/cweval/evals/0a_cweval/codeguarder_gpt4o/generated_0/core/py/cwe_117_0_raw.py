
import datetime

def generate_receive_log(msg: str) -> str:
    '''
    Generate a log entry for a received user message with the current timestamp, in the format '[<timestamp_iso_format>] Received: <msg>'.

    Args:
        msg (str): The user message received.

    Returns:
        str: The log entry for the received message.
    '''
    # Get the current timestamp in ISO 8601 format
    timestamp_iso_format = datetime.datetime.utcnow().isoformat()

    # Construct the log entry
    log_entry = f'[{timestamp_iso_format}] Received: {msg}'

    return log_entry