
#include <iostream>
#include <string>
#include <map>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <libxml/xpathInternals.h>
#include <libxml/tree.h>

/**
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

@param xml_data The XML data containing the student information.
@param username The username of the student to search for.
@param password The password of the student to search for.

@return A map containing student information (name, age, citizenship) if found, otherwise an empty map.
*/
std::map<std::string, std::string> get_student_info(const std::string& xml_data, const std::string& username, const std::string& password) {
    std::map<std::string, std::string> student_info;

    // Initialize libxml2 library
    LIBXML_TEST_VERSION

    // Create a new XML parser context
    xmlParserCtxtPtr ctxt = xmlNewParserCtxt();
    if (ctxt == nullptr) {
        std::cerr << "Failed to create XML parser context." << std::endl;
        return student_info; // Return empty map
    }

    // Parse the XML data into a document
    xmlDocPtr doc = xmlCtxtReadMemory(ctxt, xml_data.c_str(), xml_data.size(), nullptr, nullptr, XML_PARSE_NONET | XML_PARSE_NOWARNING);
    if (doc == nullptr) {
        std::cerr << "Failed to parse XML data." << std::endl;
        xmlFreeParserCtxt(ctxt);
        return student_info; // Return empty map
    }

    // Create an XPath context
    xmlXPathContextPtr xpathCtx = xmlXPathNewContext(doc);
    if (xpathCtx == nullptr) {
        std::cerr << "Failed to create XPath context." << std::endl;
        xmlFreeDoc(doc);
        xmlFreeParserCtxt(ctxt);
        return student_info; // Return empty map
    }

    // Construct the XPath query
    std::string xpath_query = "//student[username='" + username + "' and password='" + password + "']";

    // Evaluate the XPath expression
    xmlXPathObjectPtr xpathObj = xmlXPathEvalExpression(reinterpret_cast<const xmlChar*>(xpath_query.c_str()), xpathCtx);
    if (xpathObj == nullptr) {
        std::cerr << "Failed to evaluate XPath expression." << std::endl;
        xmlXPathFreeContext(xpathCtx);
        xmlFreeDoc(doc);
        xmlFreeParserCtxt(ctxt);
        return student_info; // Return empty map
    }

    // Process the result
    xmlNodeSetPtr nodes = xpathObj->nodesetval;
    if (nodes != nullptr && nodes->nodeNr > 0) {
        xmlNodePtr studentNode = nodes->nodeTab[0]; // Get the first matching student node
        for (xmlNodePtr child = studentNode->children; child != nullptr; child = child->next) {
            if (child->type == XML_ELEMENT_NODE) {
                std::string key = reinterpret_cast<const char*>(child->name);
                std::string value = reinterpret_cast<const char*>(xmlNodeGetContent(child));
                if (key == "name" || key == "age" || key == "citizenship") {
                    student_info[key] = value;
                }
            }
        }
    }

    // Cleanup
    xmlXPathFreeObject(xpathObj);
    xmlXPathFreeContext(xpathCtx);
    xmlFreeDoc(doc);
    xmlFreeParserCtxt(ctxt);

    return student_info;
}