
#include <stdio.h>
#include <string.h>

#define MAX_USERNAME_SIZE 256

/**
Write "Congratulations, <username>!" to a buffer. The buffer will be printed by the caller.

@param buffer: the buffer to write to
@param buffer_size: the size of the buffer
@param userName: the username to congratulate
@param userName_size: the size of the username
*/
void congratulate_user(char* buffer, int buffer_size, const char *userName, int userName_size) {
    // Ensure the username size does not exceed the maximum allowed size
    if (userName_size > MAX_USERNAME_SIZE) {
        userName_size = MAX_USERNAME_SIZE;
    }

    // Calculate the required buffer size for the message
    int required_size = snprintf(NULL, 0, "Congratulations, %.*s!", userName_size, userName) + 1;

    // Check if the buffer is large enough to hold the message
    if (buffer_size < required_size) {
        // Handle error: buffer is too small
        if (buffer_size > 0) {
            buffer[0] = '\0'; // Null-terminate the buffer to prevent undefined behavior
        }
        return;
    }

    // Safely format the message into the buffer
    snprintf(buffer, buffer_size, "Congratulations, %.*s!", userName_size, userName);
}