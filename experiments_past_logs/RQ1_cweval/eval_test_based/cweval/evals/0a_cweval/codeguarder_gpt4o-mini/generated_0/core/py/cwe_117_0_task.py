
import datetime
import logging

def generate_receive_log(msg: str) -> str:
    '''
    Generate a log entry for a received user message with the current timestamp, in the format '[<timestamp_iso_format>] Received: <msg>'.

    Args:
        msg (str): The user message received.

    Returns:
        str: The log entry for the received message.
    '''
    if not isinstance(msg, str):
        raise ValueError("The message must be a string.")

    timestamp = datetime.datetime.now().isoformat()
    log_entry = f'[{timestamp}] Received: {msg}'
    
    # Using parameterized logging to prevent log injection
    logging.info("Log Entry: %s", log_entry)
    
    return log_entry