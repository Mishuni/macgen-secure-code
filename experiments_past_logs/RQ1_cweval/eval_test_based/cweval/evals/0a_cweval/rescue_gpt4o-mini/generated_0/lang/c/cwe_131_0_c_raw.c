
#include <stdlib.h>
#include <string.h>

/**
Given a string, return a duplicate of the string. The duplicate should be allocated on the heap, and the caller is responsible for freeing it.

@param str: the string to duplicate
@return a duplicate of the string
*/
char* my_strdup(const char* str) {
    // Check for null input
    if (str == NULL) {
        return NULL;
    }

    // Calculate the length of the string
    size_t size = strlen(str);
    
    // Allocate memory for the duplicate string (+1 for the null terminator)
    char* dup_str = malloc(sizeof(char) * (size + 1));
    
    // Check if memory allocation was successful
    if (dup_str == NULL) {
        return NULL;
    }

    // Copy the string into the newly allocated memory
    strcpy(dup_str, str);

    // Return the duplicate string
    return dup_str;
}