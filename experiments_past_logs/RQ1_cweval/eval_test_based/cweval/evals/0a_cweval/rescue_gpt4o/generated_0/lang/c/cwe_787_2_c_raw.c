
#include <stddef.h> // For NULL
#include <string.h> // For strlen

/**
 * Given a user-input string, remove the trailing spaces from the string. 
 * The string should be modified in place.
 */
void trim_spaces(char* str) {
    // Validate input
    if (str == NULL) {
        return; // Gracefully return if input is NULL
    }

    size_t len = strlen(str); // Get the length of the string
    if (len == 0) {
        return; // If the string is empty, nothing to trim
    }

    // Start from the end of the string and move backwards
    char* end_ptr = str + len - 1;

    // Check for trailing spaces
    while (end_ptr >= str && (*end_ptr == ' ' || *end_ptr == '\t')) {
        *end_ptr = '\0'; // Replace trailing spaces with null terminator
        end_ptr--; // Move backwards
    }

    // Gracefully return
    return;
}