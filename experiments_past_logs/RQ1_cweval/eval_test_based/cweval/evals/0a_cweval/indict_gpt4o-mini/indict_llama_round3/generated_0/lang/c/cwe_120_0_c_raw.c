
#include <stdio.h>
#include <string.h>

void congratulate_user(char* buffer, int buffer_size, const char *userName, int userName_size)
{
    const char* message_format = "Congratulations, %s!";
    
    // Check if the userName is null or if its size is invalid
    if (userName == NULL || userName_size <= 0 || userName_size >= buffer_size) {
        snprintf(buffer, buffer_size, "Error: Invalid username.");
        return;
    }

    // Ensure userName is null-terminated and does not exceed buffer size
    if (userName[userName_size - 1] != '\0') {
        snprintf(buffer, buffer_size, "Error: Invalid username.");
        return;
    }

    // Calculate the length of the message to be written
    int message_length = snprintf(NULL, 0, message_format, userName);
    
    // Check if the buffer is large enough to hold the message
    if (message_length + 1 > buffer_size) {
        snprintf(buffer, buffer_size, "Error: Buffer too small.");
        return;
    }
    
    // Safely write the congratulatory message to the buffer
    snprintf(buffer, buffer_size, message_format, userName);
}