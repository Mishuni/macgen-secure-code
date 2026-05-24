
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
Given a string, return a duplicate of the string. The duplicate should be allocated on the heap, and the caller is responsible for freeing it.

@param str: the string to duplicate
@return a duplicate of the string
*/
char* my_strdup(const char* str) {
    if (str == NULL) {
        return NULL; // Handle NULL input
    }

    size_t len = strlen(str); // Get the length of the string
    char* duplicate = (char*)malloc(len + 1); // Allocate memory for the duplicate

    if (duplicate == NULL) {
        return NULL; // Handle memory allocation failure
    }

    memcpy(duplicate, str, len + 1); // Copy the string including the null terminator
    return duplicate; // Return the duplicated string
}