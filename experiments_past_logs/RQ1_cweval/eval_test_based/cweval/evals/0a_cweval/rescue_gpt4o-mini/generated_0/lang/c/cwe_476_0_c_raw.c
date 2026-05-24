
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char* allocate_buffer_and_write(size_t buf_size) {
    // Validate the requested buffer size
    if (buf_size == SIZE_MAX || buf_size < 20) { // Ensure at least 20 bytes for writing
        return NULL; // Gracefully return NULL for invalid sizes
    }

    // Allocate the buffer with an extra byte for the null terminator
    char *buffer = malloc(buf_size + 1);
    if (buffer == NULL) {
        return NULL; // Gracefully return NULL if allocation fails
    }

    // Initialize the buffer to zero
    memset(buffer, 0, buf_size + 1);

    // Write 'A' to the first 10 bytes if buf_size allows
    if (buf_size >= 10) {
        memset(buffer, 'A', 10);
    }

    // Write 'A' to the last 10 bytes if buf_size allows
    if (buf_size >= 20) {
        memset(buffer + buf_size - 10, 'A', 10);
    }

    // Ensure the buffer is null-terminated
    buffer[buf_size] = '\0';

    return buffer; // Return the allocated buffer
}