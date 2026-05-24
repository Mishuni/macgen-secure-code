#include <stdlib.h>
#include <string.h>

char* my_strdup(const char* str) {
    if (str == NULL) {
        return NULL;
    }

    size_t len = strlen(str);
    // Check for potential overflow
    if (len + 1 == 0) {
        return NULL;
    }

    char* duplicate = (char*)malloc(len + 1);
    if (duplicate == NULL) {
        return NULL;
    }

    // Use strncpy to avoid potential buffer overflow
    strncpy(duplicate, str, len + 1);

    return duplicate;
}