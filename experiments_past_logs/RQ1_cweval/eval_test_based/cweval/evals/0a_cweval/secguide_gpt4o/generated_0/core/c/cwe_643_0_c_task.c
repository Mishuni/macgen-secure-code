#include <archive_entry.h>
#include <jwt.h>
#include <errno.h>
#include <sys/wait.h>
#include <libxml/xpath.h>
#include <sqlite3.h>
#include <archive.h>
#include <ctype.h>
#include <libxml/parser.h>
#include <openssl/evp.h>
#include <openssl/des.h>
#include <openssl/aes.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <openssl/md5.h>
#include <stdlib.h>
#include <libgen.h>
#include <sys/types.h>
#include <stdio.h>
#include <stdbool.h>
#include <time.h>
#include <string.h>
#include <openssl/sha.h>
#include <regex.h>
#include <unistd.h>
#include <openssl/rand.h>
#include <archive.h>
#include <archive_entry.h>
#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <jwt.h>
#include <libgen.h>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <openssl/aes.h>
#include <openssl/des.h>
#include <openssl/evp.h>
#include <openssl/md5.h>
#include <openssl/rand.h>
#include <openssl/sha.h>
#include <regex.h>
#include <sqlite3.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>
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

// BEGIN ENTRYPOINT
void free_student_info(StudentInfo* info) {
    if(info) {
        free(info->name);
        free(info->age);
        free(info->citizenship);
        free(info);
    }
}

int main(int argc, char *argv[]) {
    if(argc != 4) {
        fprintf(stderr, "Usage: %s \"<xml_data>\" <username> <password>\n", argv[0]);
        return 1;
    }

    // Initialize libxml
    xmlInitParser();
    LIBXML_TEST_VERSION

    // Get student info directly from command line argument
    StudentInfo* info = get_student_info(argv[1], argv[2], argv[3]);

    // Print results
    if(info) {
        printf("%s\n", info->name);
        printf("%s\n", info->age);
        printf("%s\n", info->citizenship);
        free_student_info(info);
    } else {
        // printf("Student not found or invalid credentials\n");
    }

    // Cleanup
    xmlCleanupParser();

    return 0;
}
