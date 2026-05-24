
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char* allocate_buffer_and_write(size_t buf_size) {
    // Check for potential integer overflow in buffer size calculation
    if (buf_size < 20) {
        return NULL; // Not enough space to write 'A' in the first and last 10 bytes
    }

    // Allocate memory for the buffer
    char *buffer = (char *)malloc(buf_size);
    if (buffer == NULL) {
        return NULL; // Memory allocation failed
    }

    // Initialize the buffer to zero
    memset(buffer, 0, buf_size);

    // Write 'A' to the first 10 bytes
    memset(buffer, 'A', 10);

    // Write 'A' to the last 10 bytes
    if (buf_size >= 10) {
        memset(buffer + buf_size - 10, 'A', 10);
    }

    return buffer;
}