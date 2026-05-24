from typing import Dict
from lxml import etree

def get_student_info(
    xml_data: str, username: str, password: str
) -> Dict[str, str] | None:
    try:
        root = etree.fromstring(xml_data)
        evaluator = etree.XPathEvaluator(root)
        evaluator.register_variable("username", username)
        evaluator.register_variable("password", password)
        xpath_query = ".//student[username=$username and password=$password]"
        student_element = evaluator(xpath_query)
        
        if student_element:
            student = student_element[0]
            return {
                "name": student.findtext("name"),
                "citizenship": student.findtext("citizenship"),
                "age": student.findtext("age"),
            }
    except etree.XMLSyntaxError:
        return None
    return None