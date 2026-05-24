import re
from typing import Tuple

def check_email(email: str) -> Tuple[bool, str]:
    email_pattern = r"^(?=.{1,256})(?=.{1,64}@.{1,255}$)(?:(?!\.)[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?!-)[A-Za-z0-9-]+(?:(?:\.[A-Za-z0-9-]+)*)|(?:\[(?:(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\]))$"
    is_valid = re.match(email_pattern, email) is not None
    return is_valid, email_pattern