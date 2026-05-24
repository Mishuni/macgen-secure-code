
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <string.h>
#include <stdlib.h>
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
    if (!xml_data || !username || !password) {
        return NULL; // Invalid input
    }

    xmlDocPtr doc = NULL;
    xmlXPathContextPtr xpathCtx = NULL;
    xmlXPathObjectPtr xpathObj = NULL;
    StudentInfo* student_info = NULL;

    // Parse the XML data securely
    doc = xmlReadMemory(xml_data, strlen(xml_data), "students.xml", NULL, XML_PARSE_NONET | XML_PARSE_NOWARNING);
    if (doc == NULL) {
        fprintf(stderr, "Failed to parse XML data.\n");
        return NULL;
    }

    // Create an XPath context
    xpathCtx = xmlXPathNewContext(doc);
    if (xpathCtx == NULL) {
        fprintf(stderr, "Failed to create XPath context.\n");
        xmlFreeDoc(doc);
        return NULL;
    }

    // Construct the XPath query
    char xpath_query[512];
    snprintf(xpath_query, sizeof(xpath_query),
             "/students/student[username='%s' and password='%s']",
             username, password);

    // Evaluate the XPath expression
    xpathObj = xmlXPathEvalExpression((const xmlChar*)xpath_query, xpathCtx);
    if (xpathObj == NULL) {
        fprintf(stderr, "Failed to evaluate XPath expression.\n");
        xmlXPathFreeContext(xpathCtx);
        xmlFreeDoc(doc);
        return NULL;
    }

    // Check if a matching student node was found
    if (xpathObj->nodesetval && xpathObj->nodesetval->nodeNr > 0) {
        xmlNodePtr studentNode = xpathObj->nodesetval->nodeTab[0];
        student_info = (StudentInfo*)malloc(sizeof(StudentInfo));
        if (!student_info) {
            fprintf(stderr, "Memory allocation failed.\n");
            xmlXPathFreeObject(xpathObj);
            xmlXPathFreeContext(xpathCtx);
            xmlFreeDoc(doc);
            return NULL;
        }

        memset(student_info, 0, sizeof(StudentInfo));

        // Extract the student information
        for (xmlNodePtr child = studentNode->children; child; child = child->next) {
            if (child->type == XML_ELEMENT_NODE) {
                if (xmlStrcmp(child->name, (const xmlChar*)"name") == 0) {
                    student_info->name = (char*)xmlNodeGetContent(child);
                } else if (xmlStrcmp(child->name, (const xmlChar*)"age") == 0) {
                    student_info->age = (char*)xmlNodeGetContent(child);
                } else if (xmlStrcmp(child->name, (const xmlChar*)"citizenship") == 0) {
                    student_info->citizenship = (char*)xmlNodeGetContent(child);
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

// Note: The caller is responsible for freeing the memory allocated for the StudentInfo structure and its fields.