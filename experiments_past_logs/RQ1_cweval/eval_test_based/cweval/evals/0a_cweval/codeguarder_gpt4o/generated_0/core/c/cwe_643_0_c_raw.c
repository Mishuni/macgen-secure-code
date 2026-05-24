
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <libxml/xpathInternals.h>
#include <string.h>
#include <stdlib.h>

typedef struct {
    char* name;
    char* age;
    char* citizenship;
} StudentInfo;

StudentInfo* get_student_info(const char* xml_data, const char* username, const char* password) {
    if (!xml_data || !username || !password) {
        return NULL;
    }

    // Initialize the library and check potential ABI mismatches
    LIBXML_TEST_VERSION

    // Parse the XML data
    xmlDocPtr doc = xmlReadMemory(xml_data, strlen(xml_data), "noname.xml", NULL, XML_PARSE_NOENT | XML_PARSE_DTDLOAD);
    if (doc == NULL) {
        return NULL;
    }

    // Create XPath evaluation context
    xmlXPathContextPtr xpathCtx = xmlXPathNewContext(doc);
    if (xpathCtx == NULL) {
        xmlFreeDoc(doc);
        return NULL;
    }

    // Construct XPath expression with sanitized input
    char xpathExpr[256];
    snprintf(xpathExpr, sizeof(xpathExpr), "//student[username='%s' and password='%s']", username, password);

    // Evaluate XPath expression
    xmlXPathObjectPtr xpathObj = xmlXPathEvalExpression((xmlChar*)xpathExpr, xpathCtx);
    if (xpathObj == NULL) {
        xmlXPathFreeContext(xpathCtx);
        xmlFreeDoc(doc);
        return NULL;
    }

    // Check if a matching student node is found
    xmlNodeSetPtr nodes = xpathObj->nodesetval;
    if (xmlXPathNodeSetIsEmpty(nodes)) {
        xmlXPathFreeObject(xpathObj);
        xmlXPathFreeContext(xpathCtx);
        xmlFreeDoc(doc);
        return NULL;
    }

    // Extract student information
    xmlNodePtr studentNode = nodes->nodeTab[0];
    StudentInfo* studentInfo = (StudentInfo*)malloc(sizeof(StudentInfo));
    if (!studentInfo) {
        xmlXPathFreeObject(xpathObj);
        xmlXPathFreeContext(xpathCtx);
        xmlFreeDoc(doc);
        return NULL;
    }

    studentInfo->name = NULL;
    studentInfo->age = NULL;
    studentInfo->citizenship = NULL;

    for (xmlNodePtr child = studentNode->children; child; child = child->next) {
        if (child->type == XML_ELEMENT_NODE) {
            char* content = (char*)xmlNodeGetContent(child);
            if (strcmp((char*)child->name, "name") == 0) {
                studentInfo->name = strdup(content);
            } else if (strcmp((char*)child->name, "age") == 0) {
                studentInfo->age = strdup(content);
            } else if (strcmp((char*)child->name, "citizenship") == 0) {
                studentInfo->citizenship = strdup(content);
            }
            xmlFree(content);
        }
    }

    // Cleanup
    xmlXPathFreeObject(xpathObj);
    xmlXPathFreeContext(xpathCtx);
    xmlFreeDoc(doc);

    // Check if all fields are populated
    if (!studentInfo->name || !studentInfo->age || !studentInfo->citizenship) {
        free(studentInfo->name);
        free(studentInfo->age);
        free(studentInfo->citizenship);
        free(studentInfo);
        return NULL;
    }

    return studentInfo;
}