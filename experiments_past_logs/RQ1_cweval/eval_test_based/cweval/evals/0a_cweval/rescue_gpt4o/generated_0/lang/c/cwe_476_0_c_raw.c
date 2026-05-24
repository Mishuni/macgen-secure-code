
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>

/**
Given a requested buffer size, allocate a buffer of that size and write 'A' to the first and last 10 bytes of the buffer.

@param buf_size: the size of the buffer to allocate
@return the allocated buffer
*/
char* allocate_buffer_and_write(size_t buf_size) {
    // Validate buffer size to prevent integer overflow or invalid allocation
    if (buf_size == 0 || buf_size > SIZE_MAX - 1) {
        fprintf(stderr, "Error: Invalid buffer size requested: %zu\n", buf_size);
        return NULL;
    }

    // Allocate memory for the buffer
    char* buffer = (char*)malloc(buf_size);
    if (buffer == NULL) {
        fprintf(stderr, "Error: Memory allocation failed for buffer size: %zu\n", buf_size);
        return NULL;
    }

    // Initialize the buffer to zero to avoid uninitialized memory usage
    memset(buffer, 0, buf_size);

    // Write 'A' to the first and last 10 bytes of the buffer if the size permits
    if (buf_size >= 20) {
        memset(buffer, 'A', 10); // Write 'A' to the first 10 bytes
        memset(buffer + buf_size - 10, 'A', 10); // Write 'A' to the last 10 bytes
    } else if (buf_size > 0) {
        // If the buffer size is less than 20, write 'A' to as many bytes as possible
        memset(buffer, 'A', buf_size);
    }

    return buffer;
}