
#include <iostream>
#include <string>
#include <map>
#include <stdexcept>
#include <sstream>
#include <pugixml.hpp>

std::map<std::string, std::string> get_student_info(const std::string& xml_data, const std::string& username, const std::string& password) {
    std::map<std::string, std::string> student_info;

    // Load the XML data into a pugi::xml_document
    pugi::xml_document doc;
    pugi::xml_parse_result result = doc.load_string(xml_data.c_str());

    if (!result) {
        throw std::runtime_error("Failed to parse XML data");
    }

    // Construct a safe XPath query
    std::ostringstream xpath_query;
    xpath_query << "/students/student[username='" << pugi::xpath_string(username.c_str()) 
                << "' and password='" << pugi::xpath_string(password.c_str()) << "']";

    // Execute the XPath query
    pugi::xpath_node student_node = doc.select_node(xpath_query.str().c_str());

    if (student_node) {
        pugi::xml_node student = student_node.node();
        student_info["name"] = student.child("name").text().as_string();
        student_info["citizenship"] = student.child("citizenship").text().as_string();
        student_info["age"] = student.child("age").text().as_string();
    }

    return student_info;
}