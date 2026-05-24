
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

/**
Given a string, return a duplicate of the string. The duplicate should be allocated on the heap, and the caller is responsible for freeing it.

@param str: the string to duplicate
@return a duplicate of the string
*/
char* my_strdup(const char* str) {
    if (str == NULL) {
        return NULL;
    }

    size_t len = strlen(str) + 1; // Include space for null terminator

    // Check for potential integer overflow
    if (len == 0 || len > SIZE_MAX) {
        return NULL;
    }

    char* duplicate = (char*)malloc(len);
    if (!duplicate) {
        return NULL; // Allocation failed
    }

    memcpy(duplicate, str, len); // Use memcpy to ensure the exact number of bytes is copied
    return duplicate;
}