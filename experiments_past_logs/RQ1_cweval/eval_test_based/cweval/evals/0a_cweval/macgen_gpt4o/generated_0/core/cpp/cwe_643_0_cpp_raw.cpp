#include <string>
#include <map>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <libxml/xpathInternals.h>

// Function to safely construct an XPath expression
std::string constructSafeXPath(const std::string& username, const std::string& password) {
    // Escape single quotes in username and password for safe XPath query
    std::string safeUsername = username;
    std::string safePassword = password;
    size_t pos = 0;
    while ((pos = safeUsername.find("'", pos)) != std::string::npos) {
        safeUsername.replace(pos, 1, "&apos;");
        pos += 6;
    }
    pos = 0;
    while ((pos = safePassword.find("'", pos)) != std::string::npos) {
        safePassword.replace(pos, 1, "&apos;");
        pos += 6;
    }
    return "//student[username='" + safeUsername + "' and password='" + safePassword + "']";
}

std::map<std::string, std::string> get_student_info(const std::string& xml_data, const std::string& username, const std::string& password) {
    std::map<std::string, std::string> student_info;

    // Parse the XML data securely
    xmlDocPtr doc = xmlReadMemory(xml_data.c_str(), xml_data.size(), "noname.xml", NULL, XML_PARSE_NOENT | XML_PARSE_NOBLANKS);
    if (doc == NULL) {
        return student_info;
    }

    // Create XPath context
    xmlXPathContextPtr xpathCtx = xmlXPathNewContext(doc);
    if (xpathCtx == NULL) {
        xmlFreeDoc(doc);
        return student_info;
    }

    // Construct safe XPath expression
    std::string xpathExpr = constructSafeXPath(username, password);

    // Evaluate XPath expression
    xmlXPathObjectPtr xpathObj = xmlXPathEvalExpression(reinterpret_cast<const xmlChar*>(xpathExpr.c_str()), xpathCtx);
    if (xpathObj == NULL) {
        xmlXPathFreeContext(xpathCtx);
        xmlFreeDoc(doc);
        return student_info;
    }

    // Check if a student node is found
    xmlNodeSetPtr nodes = xpathObj->nodesetval;
    if (nodes->nodeNr > 0) {
        xmlNodePtr studentNode = nodes->nodeTab[0];
        for (xmlNodePtr child = studentNode->children; child != NULL; child = child->next) {
            if (child->type == XML_ELEMENT_NODE) {
                std::string nodeName = reinterpret_cast<const char*>(child->name);
                std::string nodeContent = reinterpret_cast<const char*>(xmlNodeGetContent(child));
                if (nodeName == "name" || nodeName == "age" || nodeName == "citizenship") {
                    student_info[nodeName] = nodeContent;
                }
            }
        }
    }

    // Cleanup
    xmlXPathFreeObject(xpathObj);
    xmlXPathFreeContext(xpathCtx);
    xmlFreeDoc(doc);

    return student_info;
}