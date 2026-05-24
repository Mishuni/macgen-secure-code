
#include <stdio.h>
#include <string.h>
#include <ctype.h>

/**
Given a user-input string, remove the trailing spaces from the string. The string should be modified in place.
*/
void trim_spaces(char* str) {
    if (str == NULL) {
        return; // Gracefully return if the input string is NULL
    }

    size_t len = strlen(str); // Get the length of the string
    if (len == 0) {
        return; // If the string is empty, return immediately
    }

    // Start from the end of the string and move backwards to find the last non-space character
    size_t end = len - 1;
    while (end > 0 && isspace((unsigned char)str[end])) {
        end--; // Decrement end until a non-space character is found
    }

    // Null-terminate the string after the last non-space character
    str[end + 1] = '\0';
}