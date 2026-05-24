
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

    size_t len = strlen(str); // Get the length of the input string

    // Check for potential overflow in memory allocation
    if (len + 1 < len) {
        return NULL; // Handle size overflow
    }

    char* duplicate = (char*)malloc(len + 1); // Allocate memory for the duplicate string

    if (duplicate == NULL) {
        return NULL; // Handle memory allocation failure
    }

    // Use memcpy for potentially better performance
    memcpy(duplicate, str, len + 1); // Copy the original string to the duplicate, including the null terminator
    return duplicate; // Return the duplicate string
}