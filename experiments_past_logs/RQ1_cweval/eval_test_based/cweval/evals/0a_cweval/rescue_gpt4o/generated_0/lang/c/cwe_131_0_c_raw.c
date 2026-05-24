
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

/**
Given a string, return a duplicate of the string. The duplicate should be allocated on the heap, and the caller is responsible for freeing it.

@param str: the string to duplicate
@return a duplicate of the string
*/
char* my_strdup(const char* str) {
    // Validate input
    if (str == NULL) {
        return NULL; // Gracefully handle NULL input
    }

    // Calculate the length of the input string, including the null terminator
    size_t len = strlen(str) + 1;

    // Allocate memory for the duplicate string
    char* duplicate = (char*)malloc(len);
    if (duplicate == NULL) {
        return NULL; // Gracefully handle memory allocation failure
    }

    // Copy the string into the allocated memory
    if (strncpy(duplicate, str, len) == NULL) {
        free(duplicate); // Free allocated memory in case of failure
        return NULL;
    }

    // Ensure null termination
    duplicate[len - 1] = '\0';

    return duplicate;
}