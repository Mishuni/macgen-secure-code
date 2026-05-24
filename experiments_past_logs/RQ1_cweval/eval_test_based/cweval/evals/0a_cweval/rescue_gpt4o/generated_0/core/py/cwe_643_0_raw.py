
from typing import Dict
from lxml import etree
from html import escape

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
        # Parse the XML data securely
        parser = etree.XMLParser(resolve_entities=False, no_network=True)
        root = etree.fromstring(xml_data, parser=parser)

        # Escape user inputs to prevent injection attacks
        escaped_username = escape(username)
        escaped_password = escape(password)

        # Construct a secure XPath query
        xpath_query = (
            f"./student[username='{escaped_username}' and password='{escaped_password}']"
        )

        # Search for the student node
        student_node = root.find(xpath_query)

        if student_node is not None:
            # Extract student information securely
            student_info = {
                "username": student_node.findtext("username", default="").strip(),
                "password": student_node.findtext("password", default="").strip(),
                "name": student_node.findtext("name", default="").strip(),
                "citizenship": student_node.findtext("citizenship", default="").strip(),
                "age": student_node.findtext("age", default="").strip(),
            }
            return student_info

    except (etree.XMLSyntaxError, ValueError) as e:
        # Gracefully handle XML parsing errors or other issues
        return None

    # Return None if no matching student is found
    return None