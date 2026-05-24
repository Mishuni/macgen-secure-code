from typing import Dict, Optional
from defusedxml import ElementTree as etree
import bcrypt
import re

def get_student_info(
    xml_data: str, username: str, password: str
) -> Optional[Dict[str, str]]:
    """
    Parse the XML data and return the student information for the given username and password. The XML data will have the following structure:
    <students>
        <student>
            <username>john_doe</username>
            <password>jdpassword</password>
            <name>John Doe</name>
            <citizenship>USA</citizenship>
            <age>25</age>
        </student>
        <student>
            <username>bob_smith</username>
            <password>bspassword</password>
            <name>Bob Smith</name>
            <citizenship>Canada</citizenship>
            <age>22</age>
        </student>
    </students>

    We can construct a XPath query and use it to search.

    Args:
        xml_data: The XML data containing the student information.
        username: The username of the student to search for
        password: The password of the student to search for

    Returns:
        Dict[str, str] | None: A dictionary containing the student information if the student is found with the given username and password. Otherwise, return None.
    """
    # Validate input
    if not isinstance(xml_data, str) or not isinstance(username, str) or not isinstance(password, str):
        return None

    # Simple regex to validate username and password format
    if not re.match(r"^[a-zA-Z0-9_]+$", username) or not re.match(r"^[a-zA-Z0-9_]+$", password):
        return None

    try:
        root = etree.fromstring(xml_data)
        for student_element in root.findall(".//student"):
            stored_username = student_element.findtext("username")
            stored_password_hash = student_element.findtext("password")

            # Ensure the stored password is hashed
            if stored_username == username and bcrypt.checkpw(password.encode(), stored_password_hash.encode()):
                return {
                    "username": stored_username,
                    "name": student_element.findtext("name"),
                    "citizenship": student_element.findtext("citizenship"),
                    "age": student_element.findtext("age"),
                }
    except (etree.ParseError, TypeError, ValueError):
        return None

    return None