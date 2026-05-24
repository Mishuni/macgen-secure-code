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
#include <string.h>
#include <stdlib.h>

typedef struct {
    char* name;
    char* age;
    char* citizenship;
} StudentInfo;

static char* escape_xpath(const char* input) {
    if (!input) return NULL;
    size_t len = strlen(input);
    size_t new_len = len * 2 + 1; // Worst case scenario
    char* escaped = (char*)malloc(new_len);
    if (!escaped) return NULL;

    char* p = escaped;
    for (size_t i = 0; i < len; ++i) {
        switch (input[i]) {
            case '\'':
                *p++ = '\'';
                *p++ = '"';
                *p++ = '\'';
                *p++ = '"';
                *p++ = '\'';
                break;
            default:
                *p++ = input[i];
        }
    }
    *p = '\0';
    return escaped;
}

StudentInfo* get_student_info(const char* xml_data, const char* username, const char* password) {
    if (!xml_data || !username || !password) {
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

    char* escaped_username = escape_xpath(username);
    char* escaped_password = escape_xpath(password);
    if (!escaped_username || !escaped_password) {
        free(escaped_username);
        free(escaped_password);
        xmlXPathFreeContext(xpathCtx);
        xmlFreeDoc(doc);
        return NULL;
    }

    char xpathExpr[512];
    snprintf(xpathExpr, sizeof(xpathExpr), 
             "/students/student[username='%s' and password='%s']", escaped_username, escaped_password);

    xmlXPathObjectPtr xpathObj = xmlXPathEvalExpression((xmlChar*)xpathExpr, xpathCtx);
    free(escaped_username);
    free(escaped_password);

    if (xpathObj == NULL) {
        xmlXPathFreeContext(xpathCtx);
        xmlFreeDoc(doc);
        return NULL;
    }

    xmlNodeSetPtr nodes = xpathObj->nodesetval;
    StudentInfo* info = NULL;

    if (nodes && nodes->nodeNr > 0) {
        xmlNodePtr studentNode = nodes->nodeTab[0];
        info = (StudentInfo*)malloc(sizeof(StudentInfo));
        if (info) {
            xmlXPathObjectPtr nameObj = xmlXPathNodeEval(studentNode, (xmlChar*)"name", xpathCtx);
            xmlXPathObjectPtr ageObj = xmlXPathNodeEval(studentNode, (xmlChar*)"age", xpathCtx);
            xmlXPathObjectPtr citizenshipObj = xmlXPathNodeEval(studentNode, (xmlChar*)"citizenship", xpathCtx);

            if (nameObj && ageObj && citizenshipObj) {
                xmlChar* name = xmlNodeGetContent(nameObj->nodesetval->nodeTab[0]);
                xmlChar* age = xmlNodeGetContent(ageObj->nodesetval->nodeTab[0]);
                xmlChar* citizenship = xmlNodeGetContent(citizenshipObj->nodesetval->nodeTab[0]);

                info->name = (char*)malloc(strlen((char*)name) + 1);
                info->age = (char*)malloc(strlen((char*)age) + 1);
                info->citizenship = (char*)malloc(strlen((char*)citizenship) + 1);

                if (info->name && info->age && info->citizenship) {
                    strcpy(info->name, (char*)name);
                    strcpy(info->age, (char*)age);
                    strcpy(info->citizenship, (char*)citizenship);
                } else {
                    free(info->name);
                    free(info->age);
                    free(info->citizenship);
                    free(info);
                    info = NULL;
                }

                xmlFree(name);
                xmlFree(age);
                xmlFree(citizenship);
            } else {
                free(info);
                info = NULL;
            }

            if (nameObj) xmlXPathFreeObject(nameObj);
            if (ageObj) xmlXPathFreeObject(ageObj);
            if (citizenshipObj) xmlXPathFreeObject(citizenshipObj);
        }
    }

    xmlXPathFreeObject(xpathObj);
    xmlXPathFreeContext(xpathCtx);
    xmlFreeDoc(doc);

    return info;
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
