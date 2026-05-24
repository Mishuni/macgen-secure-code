import datetime

def generate_receive_log(msg: str) -> str:
    timestamp_iso_format = datetime.datetime.now().isoformat()
    log_entry = f'[{timestamp_iso_format}] Received: {msg}'
    return log_entry