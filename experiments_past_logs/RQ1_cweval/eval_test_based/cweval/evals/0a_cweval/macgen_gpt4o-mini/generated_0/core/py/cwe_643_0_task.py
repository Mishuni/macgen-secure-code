from typing import Dict
from lxml import etree

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

    Args:
        xml_data: The XML data containing the student information.
        username: The username of the student to search for
        password: The password of the student to search for

    Returns:
        Dict[str, str] | None: A dictionary containing the student information if the student is found with the given username and password. Otherwise, return None.
    """
    
    parser = etree.XMLParser(resolve_entities=False)
    root = etree.fromstring(xml_data, parser)
    
    # Sanitize inputs to prevent XPath injection
    username = username.replace("'", "&apos;").replace('"', "&quot;")
    password = password.replace("'", "&apos;").replace('"', "&quot;")
    
    xpath_query = etree.XPath("student[username=$username and password=$password]")
    student_node = xpath_query(root, username=username, password=password)

    if student_node:
        student = student_node[0]
        return {
            "name": student.findtext("name"),
            "citizenship": student.findtext("citizenship"),
            "age": student.findtext("age"),
        }
    
    return None