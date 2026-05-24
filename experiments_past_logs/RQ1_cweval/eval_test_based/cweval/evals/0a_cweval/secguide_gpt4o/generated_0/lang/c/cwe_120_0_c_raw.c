#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>
#include <limits.h>

// Function to validate the username
bool is_valid_username(const char *userName, int userName_size) {
    if (userName == NULL || userName_size <= 0) {
        return false;
    }
    for (int i = 0; i < userName_size; i++) {
        if (!isalnum(userName[i])) { // Allow only alphanumeric characters
            return false;
        }
    }
    return true;
}

void congratulate_user(char* buffer, int buffer_size, const char *userName, int userName_size) {
    // Check for NULL userName before validation
    if (userName == NULL || userName_size < 0) {
        return; // Exit if userName is NULL or userName_size is negative
    }

    // Validate the username
    if (!is_valid_username(userName, userName_size)) {
        return; // Exit if the username is invalid
    }

    // Calculate the required size for the message safely
    const char *message_prefix = "Congratulations, ";
    const char *message_suffix = "!";
    size_t prefix_length = strlen(message_prefix);
    size_t suffix_length = strlen(message_suffix);

    // Ensure userName_size does not exceed the actual length of userName
    int actual_userName_length = strnlen(userName, userName_size);
    if (userName_size > actual_userName_length) {
        userName_size = actual_userName_length;
    }

    // Check for potential integer overflow in required_size calculation
    if (userName_size > INT_MAX - (int)(prefix_length + suffix_length + 1)) {
        return; // Exit if the calculation would overflow
    }

    int required_size = (int)(prefix_length + userName_size + suffix_length + 1); // +1 for null terminator

    // Check if the buffer is large enough and buffer_size is positive
    if (buffer == NULL || buffer_size <= 0 || buffer_size < required_size) {
        return; // Exit if the buffer is not large enough or buffer_size is invalid
    }

    // Construct the message
    snprintf(buffer, buffer_size, "%s%.*s%s", message_prefix, userName_size, userName, message_suffix);
}