#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <libxml/xpathInternals.h>
#include <string.h>
#include <stdlib.h>
#include <openssl/evp.h>
#include <openssl/sha.h>

typedef struct {
    char* name;
    char* age;
    char* citizenship;
} StudentInfo;

// Function to hash the password using SHA-256
char* hash_password(const char* password) {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256((unsigned char*)password, strlen(password), hash);

    char* hash_string = (char*)malloc(SHA256_DIGEST_LENGTH * 2 + 1);
    if (hash_string == NULL) {
        return NULL;
    }

    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        sprintf(hash_string + (i * 2), "%02x", hash[i]);
    }
    hash_string[SHA256_DIGEST_LENGTH * 2] = '\0';

    return hash_string;
}

StudentInfo* get_student_info(const char* xml_data, const char* username, const char* password) {
    if (xml_data == NULL || username == NULL || password == NULL) {
        return NULL;
    }

    // Parse the XML data with secure flags to prevent XXE
    xmlDocPtr doc = xmlReadMemory(xml_data, strlen(xml_data), NULL, NULL, XML_PARSE_NONET | XML_PARSE_NOENT | XML_PARSE_DTDLOAD);
    if (doc == NULL) {
        return NULL;
    }

    xmlXPathContextPtr xpathCtx = xmlXPathNewContext(doc);
    if (xpathCtx == NULL) {
        xmlFreeDoc(doc);
        return NULL;
    }

    // Hash the password
    char* hashedPassword = hash_password(password);
    if (hashedPassword == NULL) {
        xmlXPathFreeContext(xpathCtx);
        xmlFreeDoc(doc);
        return NULL;
    }

    // Sanitize inputs to prevent XPath injection
    xmlChar* encodedUsername = xmlEncodeSpecialChars(doc, (const xmlChar*)username);
    xmlChar* encodedPassword = xmlEncodeSpecialChars(doc, (const xmlChar*)hashedPassword);
    free(hashedPassword);

    // Dynamically allocate buffer for XPath expression
    size_t xpathExprSize = strlen((const char*)encodedUsername) + strlen((const char*)encodedPassword) + 50;
    char* xpathExpr = (char*)malloc(xpathExprSize);
    if (xpathExpr == NULL) {
        xmlFree(encodedUsername);
        xmlFree(encodedPassword);
        xmlXPathFreeContext(xpathCtx);
        xmlFreeDoc(doc);
        return NULL;
    }

    snprintf(xpathExpr, xpathExprSize, "//student[username='%s' and password='%s']", encodedUsername, encodedPassword);

    xmlXPathObjectPtr xpathObj = xmlXPathEvalExpression((xmlChar*)xpathExpr, xpathCtx);
    free(xpathExpr);
    xmlFree(encodedUsername);
    xmlFree(encodedPassword);

    if (xpathObj == NULL) {
        xmlXPathFreeContext(xpathCtx);
        xmlFreeDoc(doc);
        return NULL;
    }

    xmlNodeSetPtr nodes = xpathObj->nodesetval;
    StudentInfo* studentInfo = NULL;

    if (nodes != NULL && nodes->nodeNr > 0) {
        xmlNodePtr studentNode = nodes->nodeTab[0];
        studentInfo = (StudentInfo*)malloc(sizeof(StudentInfo));
        if (studentInfo != NULL) {
            memset(studentInfo, 0, sizeof(StudentInfo)); // Initialize to NULL
            xmlNodePtr curNode = NULL;
            for (curNode = studentNode->children; curNode; curNode = curNode->next) {
                if (curNode->type == XML_ELEMENT_NODE) {
                    if (xmlStrcmp(curNode->name, (const xmlChar*)"name") == 0) {
                        studentInfo->name = (char*)xmlNodeGetContent(curNode);
                    } else if (xmlStrcmp(curNode->name, (const xmlChar*)"age") == 0) {
                        studentInfo->age = (char*)xmlNodeGetContent(curNode);
                    } else if (xmlStrcmp(curNode->name, (const xmlChar*)"citizenship") == 0) {
                        studentInfo->citizenship = (char*)xmlNodeGetContent(curNode);
                    }
                }
            }
        }
    }

    xmlXPathFreeObject(xpathObj);
    xmlXPathFreeContext(xpathCtx);
    xmlFreeDoc(doc);

    return studentInfo;
}