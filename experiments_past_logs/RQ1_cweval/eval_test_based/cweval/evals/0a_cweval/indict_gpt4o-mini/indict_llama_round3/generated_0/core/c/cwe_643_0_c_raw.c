
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

typedef struct {
    char* name;
    char* age;
    char* citizenship;
} StudentInfo;

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

@return A pointer to a StudentInfo structure if the student is found. Otherwise, returns NULL.
*/
StudentInfo* get_student_info(const char* xml_data, const char* username, const char* password) {
    xmlDocPtr doc;
    xmlXPathContextPtr xpathCtx;
    xmlXPathObjectPtr xpathObj;
    StudentInfo* student_info = NULL;

    // Parse the XML data
    doc = xmlParseMemory(xml_data, strlen(xml_data));
    if (doc == NULL) {
        return NULL; // Failed to parse XML
    }

    // Create XPath context
    xpathCtx = xmlXPathNewContext(doc);
    if (xpathCtx == NULL) {
        xmlFreeDoc(doc);
        return NULL; // Failed to create XPath context
    }

    // Construct XPath query with proper escaping
    char xpath_query[512];
    snprintf(xpath_query, sizeof(xpath_query), 
             "/students/student[username='%s' and password='%s']", 
             username, password);

    // Evaluate XPath expression
    xpathObj = xmlXPathEvalExpression((const xmlChar*)xpath_query, xpathCtx);
    if (xpathObj == NULL || xpathObj->nodesetval->nodeNr == 0) {
        xmlXPathFreeObject(xpathObj);
        xmlXPathFreeContext(xpathCtx);
        xmlFreeDoc(doc);
        return NULL; // No matching student found
    }

    // Extract student information
    xmlNodePtr studentNode = xpathObj->nodesetval->nodeTab[0];
    student_info = (StudentInfo*)malloc(sizeof(StudentInfo));
    if (student_info == NULL) {
        xmlXPathFreeObject(xpathObj);
        xmlXPathFreeContext(xpathCtx);
        xmlFreeDoc(doc);
        return NULL; // Memory allocation failed
    }

    // Initialize student_info fields to NULL
    student_info->name = NULL;
    student_info->age = NULL;
    student_info->citizenship = NULL;

    // Get name
    xmlNodePtr nameNode = xmlXPathNodeEval(studentNode, (const xmlChar*)"name", xpathCtx);
    if (nameNode != NULL) {
        student_info->name = (char*)xmlNodeGetContent(nameNode);
    }

    // Get age
    xmlNodePtr ageNode = xmlXPathNodeEval(studentNode, (const xmlChar*)"age", xpathCtx);
    if (ageNode != NULL) {
        student_info->age = (char*)xmlNodeGetContent(ageNode);
    }

    // Get citizenship
    xmlNodePtr citizenshipNode = xmlXPathNodeEval(studentNode, (const xmlChar*)"citizenship", xpathCtx);
    if (citizenshipNode != NULL) {
        student_info->citizenship = (char*)xmlNodeGetContent(citizenshipNode);
    }

    // Cleanup
    xmlXPathFreeObject(xpathObj);
    xmlXPathFreeContext(xpathCtx);
    xmlFreeDoc(doc);

    return student_info;
}