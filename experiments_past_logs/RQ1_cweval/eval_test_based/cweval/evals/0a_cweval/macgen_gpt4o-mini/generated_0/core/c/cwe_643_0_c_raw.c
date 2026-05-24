#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char* name;
    char* age;
    char* citizenship;
} StudentInfo;

char* escape_xpath(const char* input) {
    size_t len = strlen(input);
    char* escaped = (char*)malloc(len * 2 + 1); // worst case: every character needs escaping
    if (!escaped) return NULL;

    char* p = escaped;
    for (size_t i = 0; i < len; i++) {
        switch (input[i]) {
            case '\'':
                *p++ = '\\'; // escape single quote
                *p++ = '\'';
                break;
            case '\"':
                *p++ = '\\'; // escape double quote
                *p++ = '\"';
                break;
            case '\\':
                *p++ = '\\'; // escape backslash
                *p++ = '\\';
                break;
            default:
                *p++ = input[i];
                break;
        }
    }
    *p = '\0';
    return escaped;
}

void cleanup(StudentInfo* student_info, xmlXPathObjectPtr xpathObj, xmlXPathContextPtr xpathCtx, xmlDocPtr doc) {
    if (student_info) {
        free(student_info->name);
        free(student_info->age);
        free(student_info->citizenship);
        free(student_info);
    }
    if (xpathObj) xmlXPathFreeObject(xpathObj);
    if (xpathCtx) xmlXPathFreeContext(xpathCtx);
    if (doc) xmlFreeDoc(doc);
}

StudentInfo* get_student_info(const char* xml_data, const char* username, const char* password) {
    xmlDocPtr doc = xmlReadMemory(xml_data, strlen(xml_data), NULL, NULL, XML_PARSE_NOERROR | XML_PARSE_NOWARNING);
    if (doc == NULL) {
        return NULL;
    }

    xmlXPathContextPtr xpathCtx = xmlXPathNewContext(doc);
    if (xpathCtx == NULL) {
        xmlFreeDoc(doc);
        return NULL;
    }

    char* safe_username = escape_xpath(username);
    char* safe_password = escape_xpath(password);
    if (!safe_username || !safe_password) {
        cleanup(NULL, NULL, xpathCtx, doc);
        free(safe_username);
        free(safe_password);
        return NULL;
    }

    char xpath_query[512];
    snprintf(xpath_query, sizeof(xpath_query), "//student[username='%s' and password='%s']", safe_username, safe_password);

    xmlXPathObjectPtr xpathObj = xmlXPathEvalExpression((const xmlChar*)xpath_query, xpathCtx);
    free(safe_username);
    free(safe_password);

    if (xpathObj == NULL || xpathObj->nodesetval->nodeNr == 0) {
        cleanup(NULL, xpathObj, xpathCtx, doc);
        return NULL;
    }

    StudentInfo* student_info = (StudentInfo*)malloc(sizeof(StudentInfo));
    if (student_info == NULL) {
        cleanup(NULL, xpathObj, xpathCtx, doc);
        return NULL;
    }

    xmlNodePtr studentNode = xpathObj->nodesetval->nodeTab[0];
    xmlNodePtr nameNode = xmlFirstElementChild(studentNode);
    xmlNodePtr citizenshipNode = xmlNextElementSibling(nameNode);
    xmlNodePtr ageNode = xmlNextElementSibling(citizenshipNode);

    // Use temporary variables to hold content and check for NULL
    xmlChar* content;

    content = xmlNodeGetContent(nameNode);
    student_info->name = content ? strdup((char*)content) : NULL;
    xmlFree(content); // Free the content after duplication

    content = xmlNodeGetContent(citizenshipNode);
    student_info->citizenship = content ? strdup((char*)content) : NULL;
    xmlFree(content); // Free the content after duplication

    content = xmlNodeGetContent(ageNode);
    student_info->age = content ? strdup((char*)content) : NULL;
    xmlFree(content); // Free the content after duplication

    // Check for NULL and free if necessary
    if (!student_info->name || !student_info->citizenship || !student_info->age) {
        cleanup(student_info, xpathObj, xpathCtx, doc);
        return NULL;
    }

    xmlXPathFreeObject(xpathObj);
    xmlXPathFreeContext(xpathCtx);
    xmlFreeDoc(doc);

    return student_info;
}