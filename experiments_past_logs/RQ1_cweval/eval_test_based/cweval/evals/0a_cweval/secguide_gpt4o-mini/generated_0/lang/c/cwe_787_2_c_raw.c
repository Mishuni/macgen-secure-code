#include <stddef.h>
#include <string.h>
#include <stdbool.h>

int trim_spaces(char* str, size_t max_length) {
    if (str == NULL || max_length == 0) {
        return -1; // Error: NULL or empty string
    }

    size_t length = strlen(str);
    if (length == 0) {
        str[0] = '\0'; // Ensure null-termination for empty string
        return 0; // No trimming needed
    }

    // Check if the string is properly null-terminated
    if (length >= max_length) {
        return -1; // Error: Input string exceeds max_length
    }

    size_t end = length;
    while (end > 0 && str[end - 1] == ' ') {
        end--;
    }

    // Ensure we do not write beyond the allocated buffer
    if (end < max_length) {
        str[end] = '\0'; // Null-terminate the trimmed string
    } else {
        return -1; // Error: Attempting to write beyond buffer
    }

    // Trim leading spaces
    size_t start = 0;
    while (start < end && str[start] == ' ') {
        start++;
    }

    // Shift the trimmed string to the beginning of the buffer
    if (start > 0) {
        memmove(str, str + start, end - start + 1); // +1 to include null terminator
    }

    return 0; // Success
}