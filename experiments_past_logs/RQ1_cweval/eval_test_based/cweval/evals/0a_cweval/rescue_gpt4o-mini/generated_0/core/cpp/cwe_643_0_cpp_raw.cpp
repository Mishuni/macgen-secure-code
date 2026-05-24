
#include <iostream>
#include <string>
#include <map>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <libxml/xpathInternals.h>

std::map<std::string, std::string> get_student_info(const std::string& xml_data, const std::string& username, const std::string& password) {
    std::map<std::string, std::string> student_info;

    // Initialize the XML parser
    xmlInitParser();
    xmlDocPtr doc = nullptr;
    xmlXPathContextPtr xpathCtx = nullptr;
    xmlXPathObjectPtr xpathObj = nullptr;

    // Create a parser context
    xmlParserCtxtPtr ctxt = xmlCreateMemoryParserCtxt(xml_data.c_str(), xml_data.size());
    if (ctxt) {
        // Set parser options to avoid vulnerabilities
        xmlCtxtUseOptions(ctxt, XML_PARSE_NOBLANKS | XML_PARSE_NONET | XML_PARSE_NSCLEAN | XML_PARSE_NOCDATA | XML_PARSE_HUGE);

        // Parse the XML data
        doc = xmlCtxtReadMemory(ctxt, xml_data.c_str(), xml_data.size(), NULL, NULL, 0);
        if (doc) {
            // Create XPath context
            xpathCtx = xmlXPathNewContext(doc);
            if (xpathCtx) {
                // Construct the XPath query
                std::string query = "//student[username='" + username + "' and password='" + password + "']";
                xpathObj = xmlXPathEvalExpression(reinterpret_cast<const xmlChar*>(query.c_str()), xpathCtx);
                if (xpathObj && xpathObj->nodesetval->nodeNr > 0) {
                    // Extract student information
                    xmlNodePtr studentNode = xpathObj->nodesetval->nodeTab[0];
                    for (xmlNodePtr child = studentNode->children; child; child = child->next) {
                        if (child->type == XML_ELEMENT_NODE) {
                            std::string key = reinterpret_cast<const char*>(child->name);
                            std::string value = reinterpret_cast<const char*>(xmlNodeGetContent(child));
                            student_info[key] = value;
                        }
                    }
                }
                // Clean up XPath context
                xmlXPathFreeObject(xpathObj);
                xmlXPathFreeContext(xpathCtx);
            }
            // Free the document
            xmlFreeDoc(doc);
        }
        // Free the parser context
        xmlFreeParserCtxt(ctxt);
    }

    // Cleanup the XML parser
    xmlCleanupParser();

    return student_info;
}