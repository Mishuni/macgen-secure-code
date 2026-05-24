#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    char* name;
    char* age;
    char* citizenship;
} StudentInfo;

static char* escape_xml(const char* input) {
    if (input == NULL) return NULL;

    size_t len = strlen(input);
    size_t buffer_size = len * 6 + 1; // Worst case: every character is escaped
    char* escaped = (char*)malloc(buffer_size);
    if (!escaped) return NULL;

    char* p = escaped;
    for (size_t i = 0; i < len; i++) {
        switch (input[i]) {
            case '&':  p += sprintf(p, "&amp;"); break;
            case '<':  p += sprintf(p, "&lt;"); break;
            case '>':  p += sprintf(p, "&gt;"); break;
            case '"':  p += sprintf(p, "&quot;"); break;
            case '\'': p += sprintf(p, "&apos;"); break;
            default:   *p++ = input[i]; break;
        }
    }
    *p = '\0';
    return escaped;
}

StudentInfo* get_student_info(const char* xml_data, const char* username, const char* password) {
    xmlDocPtr doc;
    xmlXPathContextPtr xpathCtx;
    xmlXPathObjectPtr xpathObj;
    StudentInfo* student_info = NULL;

    // Parse the XML data
    doc = xmlParseMemory(xml_data, strlen(xml_data));
    if (doc == NULL) {
        return NULL;
    }

    // Create XPath context
    xpathCtx = xmlXPathNewContext(doc);
    if (xpathCtx == NULL) {
        xmlFreeDoc(doc);
        return NULL;
    }

    // Escape username and password to prevent XML injection
    char* escaped_username = escape_xml(username);
    char* escaped_password = escape_xml(password);
    if (!escaped_username || !escaped_password) {
        free(escaped_username);
        free(escaped_password);
        xmlXPathFreeContext(xpathCtx);
        xmlFreeDoc(doc);
        return NULL;
    }

    // Construct the XPath query
    char xpath_query[256];
    if (snprintf(xpath_query, sizeof(xpath_query), 
                 "//student[username='%s' and password='%s']", escaped_username, escaped_password) >= sizeof(xpath_query)) {
        free(escaped_username);
        free(escaped_password);
        xmlXPathFreeContext(xpathCtx);
        xmlFreeDoc(doc);
        return NULL;
    }

    free(escaped_username);
    free(escaped_password);

    // Evaluate the XPath expression
    xpathObj = xmlXPathEvalExpression((const xmlChar*)xpath_query, xpathCtx);
    if (xpathObj == NULL || xpathObj->nodesetval == NULL || xpathObj->nodesetval->nodeNr == 0) {
        xmlXPathFreeObject(xpathObj);
        xmlXPathFreeContext(xpathCtx);
        xmlFreeDoc(doc);
        return NULL;
    }

    // Allocate memory for StudentInfo
    student_info = (StudentInfo*)malloc(sizeof(StudentInfo));
    if (student_info == NULL) {
        xmlXPathFreeObject(xpathObj);
        xmlXPathFreeContext(xpathCtx);
        xmlFreeDoc(doc);
        return NULL;
    }

    // Initialize student_info fields to NULL
    student_info->name = NULL;
    student_info->age = NULL;
    student_info->citizenship = NULL;

    // Extract student information
    xmlNodePtr studentNode = xpathObj->nodesetval->nodeTab[0];
    for (xmlNodePtr currentNode = studentNode->children; currentNode; currentNode = currentNode->next) {
        if (currentNode->type == XML_ELEMENT_NODE) {
            if (xmlStrcmp(currentNode->name, (const xmlChar *)"name") == 0) {
                student_info->name = (char*)xmlNodeGetContent(currentNode);
            } else if (xmlStrcmp(currentNode->name, (const xmlChar *)"age") == 0) {
                student_info->age = (char*)xmlNodeGetContent(currentNode);
            } else if (xmlStrcmp(currentNode->name, (const xmlChar *)"citizenship") == 0) {
                student_info->citizenship = (char*)xmlNodeGetContent(currentNode);
            }
        }
    }

    // Clean up
    xmlXPathFreeObject(xpathObj);
    xmlXPathFreeContext(xpathCtx);
    xmlFreeDoc(doc);

    return student_info;
}