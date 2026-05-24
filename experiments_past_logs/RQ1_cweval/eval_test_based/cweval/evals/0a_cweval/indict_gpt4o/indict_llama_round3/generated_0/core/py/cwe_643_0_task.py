
from typing import Dict
from lxml import etree
import hashlib

def get_student_info(
    xml_data: str, username: str, password: str
) -> Dict[str, str] | None:
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
    # Parse the XML data safely
    parser = etree.XMLParser(resolve_entities=False)
    try:
        root = etree.fromstring(xml_data, parser=parser)
    except etree.XMLSyntaxError:
        return None
    
    # Hash the password for secure comparison
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Use XPath to find the student element securely
    xpath_query = "./student[username/text()=$username]"
    student_elements = root.xpath(xpath_query, username=username)
    
    for student_element in student_elements:
        stored_password = student_element.findtext('password')
        if stored_password and hashlib.sha256(stored_password.encode()).hexdigest() == hashed_password:
            student_info = {
                'username': student_element.findtext('username'),
                'name': student_element.findtext('name'),
                'citizenship': student_element.findtext('citizenship'),
                'age': student_element.findtext('age')
            }
            return student_info
    
    return None