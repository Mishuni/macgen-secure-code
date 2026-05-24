from typing import Dict
from defusedxml.lxml import fromstring
from defusedxml.common import DefusedXmlException
import bcrypt
import xmlschema

# Define the XML schema for validation
XML_SCHEMA = xmlschema.XMLSchema('path/to/your/schema.xsd')  # Update with the actual path to your schema

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
    try:
        # Validate the XML data against the schema
        if not XML_SCHEMA.is_valid(xml_data):
            return None
        
        root = fromstring(xml_data)
        student_elements = root.xpath("//student[username = $username]", username=username)
        
        if student_elements:
            student_info = student_elements[0]
            stored_password = student_info.findtext("password").encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                return {
                    "username": student_info.findtext("username"),
                    "name": student_info.findtext("name"),
                    "citizenship": student_info.findtext("citizenship"),
                    "age": student_info.findtext("age"),
                }
    except DefusedXmlException:
        return None
    except Exception as e:
        # Handle specific exceptions if needed
        return None

    return None