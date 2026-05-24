#include <stdlib.h>
#include <string.h>
#include <limits.h>

/**
Given a string, return a duplicate of the string. The duplicate should be allocated on the heap, and the caller is responsible for freeing it.

@param str: the string to duplicate
@return a duplicate of the string, or NULL if str is NULL or memory allocation fails
*/
char* my_strdup(const char* str) {
    if (str == NULL) {
        return NULL;
    }

    size_t len = strlen(str);
    if (len > SIZE_MAX - 1) { // Check for potential overflow
        return NULL;
    }

    char* duplicate = malloc(len + 1);
    if (duplicate == NULL) {
        return NULL;
    }

    strcpy(duplicate, str); // Use strcpy for clarity
    return duplicate;
}