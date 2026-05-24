
#include <stdio.h>
#include <string.h>
#include <ctype.h>

void trim_spaces(char* str) {
    if (str == NULL) {
        return; // Handle null pointer input safely
    }

    size_t len = strlen(str);
    if (len == 0) {
        return; // No need to trim if the string is empty
    }

    // Find the last non-whitespace character
    size_t end = len;
    while (end > 0 && isspace((unsigned char)str[end - 1])) {
        end--;
    }

    // Null-terminate the string at the new end position
    str[end] = '\0';
}