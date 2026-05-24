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
