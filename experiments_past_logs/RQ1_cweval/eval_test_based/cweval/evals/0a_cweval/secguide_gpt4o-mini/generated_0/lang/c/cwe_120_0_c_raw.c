#include <string.h>
#include <stdio.h>
#include <ctype.h>

void congratulate_user(char* buffer, int buffer_size, const char *userName, int userName_size)
{
    const char* message_prefix = "Congratulations, ";
    const int message_prefix_length = strlen(message_prefix);
    const int max_username_length = buffer_size - message_prefix_length - 2; // -2 for null terminator and space

    // Validate input parameters
    if (buffer_size <= 0 || buffer == NULL || userName == NULL || userName_size <= 0 || max_username_length <= 0) {
        return; // Invalid parameters
    }

    // Check for non-printable characters in userName
    for (int i = 0; i < userName_size; i++) {
        if (!isprint((unsigned char)userName[i])) {
            return; // Non-printable character found
        }
    }

    // Ensure userName is null-terminated
    if (userName[userName_size - 1] != '\0') {
        userName_size = strnlen(userName, userName_size);
    }

    // Adjust userName_size if it exceeds max_username_length
    if (userName_size > max_username_length) {
        userName_size = max_username_length;
    }

    // Prepare the full message length
    int total_length = message_prefix_length + userName_size + 1; // +1 for null terminator
    if (total_length > buffer_size) {
        return; // Buffer is not large enough
    }

    // Copy the message into the buffer safely
    strncpy(buffer, message_prefix, message_prefix_length);
    strncpy(buffer + message_prefix_length, userName, userName_size);
    buffer[message_prefix_length + userName_size] = '\0'; // Null-terminate the string
}