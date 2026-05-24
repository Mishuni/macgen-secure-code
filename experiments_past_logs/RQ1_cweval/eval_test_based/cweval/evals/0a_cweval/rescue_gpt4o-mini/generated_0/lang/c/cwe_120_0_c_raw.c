
#include <stdio.h>
#include <string.h>

/**
Write "Congratulations, <username>!" to a buffer. The buffer will be printed by the caller.

@param buffer: the buffer to write to
@param buffer_size: the size of the buffer
@param userName: the username to congratulate
*/
void congratulate_user(char* buffer, int buffer_size, const char *userName, int userName_size)
{
    // Validate input parameters
    if (buffer == NULL || buffer_size <= 0 || userName == NULL || userName_size <= 0) {
        return; // Gracefully return if inputs are invalid
    }

    // Prepare the congratulatory message
    const char* message_format = "Congratulations, %s!";
    int message_length = snprintf(NULL, 0, message_format, userName); // Calculate required length

    // Check if the message can fit in the buffer
    if (message_length + 1 > buffer_size) {
        // If not, truncate the message to fit
        message_length = buffer_size - 1; // Leave space for null terminator
    }

    // Write the message to the buffer
    snprintf(buffer, buffer_size, message_format, userName);

    // Ensure the buffer is null-terminated
    buffer[message_length] = '\0';
}