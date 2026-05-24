
from typing import Dict, Optional
from lxml import etree

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
    
    # Parse the XML data with protection against XXE attacks
    parser = etree.XMLParser(resolve_entities=False)
    root = etree.fromstring(xml_data.encode("utf-8"), parser=parser)

    # Validate input credentials
    if not username or not password:
        return None

    # Construct the XPath query safely
    username_xpath = f".//student[username='{username}' and password='{password}']"
    student_node = root.xpath(username_xpath)

    if student_node:
        student_info = student_node[0]
        return {
            "name": student_info.findtext("name"),
            "citizenship": student_info.findtext("citizenship"),
            "age": student_info.findtext("age"),
        }
    
    return None