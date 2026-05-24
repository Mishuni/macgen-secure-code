#include <stddef.h>
#include <ctype.h>
#include <string.h>

// Function to remove trailing spaces from a string in place
void trim_spaces(char* str) {
    if (str == NULL) {
        return;
    }

    // Ensure the string is null-terminated
    if (memchr(str, '\0', SIZE_MAX) == NULL) {
        return;
    }

    // Calculate the length of the string
    size_t length = strlen(str);

    // Start from the end of the string and move backwards
    size_t end = length;
    while (end > 0 && isspace((unsigned char)str[end - 1])) {
        end--;
    }

    // Null-terminate the string at the new end position
    if (end < length) {
        str[end] = '\0';
    }
}