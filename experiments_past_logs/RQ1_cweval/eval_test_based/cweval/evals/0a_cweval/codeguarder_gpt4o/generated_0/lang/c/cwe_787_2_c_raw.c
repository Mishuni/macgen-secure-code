
#include <stdio.h>
#include <string.h>

/**
Given a user-input string, remove the trailing spaces from the string. The string should be modified in place.
*/
void trim_spaces(char* str) {
    if (str == NULL) return; // Check for null pointer

    size_t len = strlen(str);
    if (len == 0) return; // Check for empty string

    size_t end = len - 1;

    // Traverse the string backwards to find the first non-space character
    while (end > 0 && str[end] == ' ') {
        end--;
    }

    // If the entire string was spaces, set it to an empty string
    if (end == 0 && str[end] == ' ') {
        str[0] = '\0';
    } else {
        // Null-terminate the string after the last non-space character
        str[end + 1] = '\0';
    }
}