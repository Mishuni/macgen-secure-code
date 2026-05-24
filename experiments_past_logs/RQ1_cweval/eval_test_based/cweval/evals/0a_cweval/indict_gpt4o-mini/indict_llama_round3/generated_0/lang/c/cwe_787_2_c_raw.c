
#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <stdlib.h>

void trim_spaces(char* str) {
    if (str == NULL) {
        return;
    }

    // Create a duplicate of the input string to ensure we are working with mutable memory
    char* temp = strdup(str);
    if (temp == NULL) {
        return; // Handle memory allocation failure
    }

    // Find the length of the duplicated string
    int length = strlen(temp);
    int index = length - 1;

    // Move index back to the last non-space character
    while (index >= 0 && temp[index] == ' ') {
        index--;
    }

    // Null-terminate the string at the new end
    temp[index + 1] = '\0';

    // Copy the trimmed string back to the original string
    strcpy(str, temp);

    // Free the allocated memory for the temporary string
    free(temp);
}