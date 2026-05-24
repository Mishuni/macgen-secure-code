
#include <iostream>
#include <map>
#include <string>
#include <stdexcept>
#include <memory>
#include <libxml/parser.h>
#include <libxml/xpath.h>

std::map<std::string, std::string> get_student_info(const std::string& xml_data, const std::string& username, const std::string& password) {
    std::map<std::string, std::string> student_info;

    // Initialize the XML parser
    xmlInitParser();
    xmlDocPtr doc = xmlParseMemory(xml_data.c_str(), xml_data.size());
    if (doc == nullptr) {
        throw std::runtime_error("Failed to parse XML data");
    }

    // Create an XPath context
    xmlXPathContextPtr xpathCtx = xmlXPathNewContext(doc);
    if (xpathCtx == nullptr) {
        xmlFreeDoc(doc);
        throw std::runtime_error("Failed to create XPath context");
    }

    // Construct the XPath query with sanitized input
    std::string xpath_query = "//student[username='" + username + "' and password='" + password + "']";
    xmlXPathObjectPtr xpathObj = xmlXPathEvalExpression(reinterpret_cast<const xmlChar*>(xpath_query.c_str()), xpathCtx);
    if (xpathObj == nullptr) {
        xmlXPathFreeContext(xpathCtx);
        xmlFreeDoc(doc);
        throw std::runtime_error("Failed to evaluate XPath expression");
    }

    // Check if we found any student
    if (xpathObj->nodesetval->nodeNr > 0) {
        xmlNodePtr studentNode = xpathObj->nodesetval->nodeTab[0];

        // Extract student information
        for (xmlNodePtr child = studentNode->children; child; child = child->next) {
            if (child->type == XML_ELEMENT_NODE) {
                std::string key = reinterpret_cast<const char*>(child->name);
                std::string value = reinterpret_cast<const char*>(xmlNodeGetContent(child));
                student_info[key] = value;
            }
        }
    }

    // Cleanup
    xmlXPathFreeObject(xpathObj);
    xmlXPathFreeContext(xpathCtx);
    xmlFreeDoc(doc);
    xmlCleanupParser();

    return student_info;
}