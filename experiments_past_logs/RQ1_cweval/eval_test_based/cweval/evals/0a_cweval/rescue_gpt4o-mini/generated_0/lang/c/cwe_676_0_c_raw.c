
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
Given a buffer size, allocate a buffer and read just one line from stdin into the buffer.

@param buf_size: the size of the buffer
@return the buffer containing the line read from stdin
*/
char* read_stdin_to_buffer(int buf_size) {
    // Validate the buffer size to prevent allocation of too large a buffer
    if (buf_size <= 0 || buf_size > SIZE_MAX) {
        return NULL; // Gracefully return NULL for invalid buffer size
    }

    // Allocate the buffer
    char* buf = (char*)malloc(buf_size);
    if (buf == NULL) {
        return NULL; // Gracefully return NULL if memory allocation fails
    }

    // Read a line from stdin
    if (fgets(buf, buf_size, stdin) == NULL) {
        free(buf); // Free the buffer if reading fails
        return NULL; // Gracefully return NULL if reading fails
    }

    // Ensure the buffer is null-terminated (fgets does this, but we can check)
    size_t len = strlen(buf);
    if (len > 0 && buf[len - 1] == '\n') {
        buf[len - 1] = '\0'; // Remove the newline character if present
    }

    return buf; // Return the buffer containing the line read
}