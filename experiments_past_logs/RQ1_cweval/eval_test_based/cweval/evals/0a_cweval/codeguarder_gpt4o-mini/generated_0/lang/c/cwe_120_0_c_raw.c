
#include <stdio.h>
#include <string.h>

void congratulate_user(char* buffer, size_t buffer_size, const char *userName, size_t userName_size) {
    // Ensure the buffer is not NULL and the size is sufficient
    if (buffer == NULL || buffer_size == 0) {
        return;
    }

    // Ensure the username is not NULL and the size is valid
    if (userName == NULL || userName_size == 0 || userName_size > buffer_size - 15) {
        return;
    }

    // Create the congratulatory message
    const char *message = "Congratulations, ";
    size_t message_length = strlen(message);
    
    // Check if the buffer can hold the message and username
    if (buffer_size < message_length + userName_size + 2) { // +2 for null terminator and space
        return;
    }

    // Safely format the message into the buffer
    snprintf(buffer, buffer_size, "%s%s!", message, userName);
}