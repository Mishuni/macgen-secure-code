
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <string.h>
#include <stdlib.h>

typedef struct {
    char* name;
    char* age;
    char* citizenship;
} StudentInfo;

StudentInfo* get_student_info(const char* xml_data, const char* username, const char* password) {
    if (xml_data == NULL || username == NULL || password == NULL) {
        return NULL;
    }

    xmlDocPtr doc = xmlParseMemory(xml_data, strlen(xml_data));
    if (doc == NULL) {
        return NULL;
    }

    xmlXPathContextPtr xpathCtx = xmlXPathNewContext(doc);
    if (xpathCtx == NULL) {
        xmlFreeDoc(doc);
        return NULL;
    }

    // Construct XPath expression with proper escaping
    char xpathExpr[256];
    snprintf(xpathExpr, sizeof(xpathExpr), "//student[username='%s' and password='%s']", username, password);

    xmlXPathObjectPtr xpathObj = xmlXPathEvalExpression((const xmlChar*)xpathExpr, xpathCtx);
    if (xpathObj == NULL) {
        xmlXPathFreeContext(xpathCtx);
        xmlFreeDoc(doc);
        return NULL;
    }

    xmlNodeSetPtr nodes = xpathObj->nodesetval;
    if (xmlXPathNodeSetIsEmpty(nodes)) {
        xmlXPathFreeObject(xpathObj);
        xmlXPathFreeContext(xpathCtx);
        xmlFreeDoc(doc);
        return NULL;
    }

    xmlNodePtr studentNode = nodes->nodeTab[0];
    StudentInfo* studentInfo = (StudentInfo*)malloc(sizeof(StudentInfo));
    if (studentInfo == NULL) {
        xmlXPathFreeObject(xpathObj);
        xmlXPathFreeContext(xpathCtx);
        xmlFreeDoc(doc);
        return NULL;
    }

    studentInfo->name = NULL;
    studentInfo->age = NULL;
    studentInfo->citizenship = NULL;

    xmlNodePtr curNode = studentNode->children;
    while (curNode != NULL) {
        if (curNode->type == XML_ELEMENT_NODE) {
            xmlChar* content = xmlNodeGetContent(curNode);
            if (content == NULL) {
                free(studentInfo->name);
                free(studentInfo->age);
                free(studentInfo->citizenship);
                free(studentInfo);
                xmlXPathFreeObject(xpathObj);
                xmlXPathFreeContext(xpathCtx);
                xmlFreeDoc(doc);
                return NULL;
            }
            if (xmlStrcmp(curNode->name, (const xmlChar*)"name") == 0) {
                studentInfo->name = (char*)content;
            } else if (xmlStrcmp(curNode->name, (const xmlChar*)"age") == 0) {
                studentInfo->age = (char*)content;
            } else if (xmlStrcmp(curNode->name, (const xmlChar*)"citizenship") == 0) {
                studentInfo->citizenship = (char*)content;
            } else {
                xmlFree(content);
            }
        }
        curNode = curNode->next;
    }

    xmlXPathFreeObject(xpathObj);
    xmlXPathFreeContext(xpathCtx);
    xmlFreeDoc(doc);

    return studentInfo;
}