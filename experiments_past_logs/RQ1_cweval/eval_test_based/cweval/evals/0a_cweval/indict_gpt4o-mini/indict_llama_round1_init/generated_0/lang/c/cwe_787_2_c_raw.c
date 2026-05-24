
#include <stdio.h>
#include <string.h>

void trim_spaces(char* str) {
    if (str == NULL) {
        return;
    }

    int length = strlen(str);
    int index = length - 1;

    // Move index back to the last non-space character
    while (index >= 0 && str[index] == ' ') {
        index--;
    }

    // Null-terminate the string at the new end
    str[index + 1] = '\0';
}