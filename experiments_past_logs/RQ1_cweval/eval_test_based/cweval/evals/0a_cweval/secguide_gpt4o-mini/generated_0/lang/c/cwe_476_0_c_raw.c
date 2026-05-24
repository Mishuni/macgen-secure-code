#include <stdlib.h>
#include <string.h>
#include <limits.h>

char* allocate_buffer_and_write(size_t buf_size) {
    if (buf_size < 20) {
        return NULL; // Ensure the buffer is large enough to write to the first and last 10 bytes
    }

    // Check for potential overflow and invalid sizes
    if (buf_size > SIZE_MAX - 1 || buf_size <= 0) {
        return NULL; // Prevent allocation of excessively large or invalid buffers
    }

    char* buffer = malloc(buf_size); // No cast needed
    if (buffer == NULL) {
        return NULL; // Handle memory allocation failure
    }

    memset(buffer, 0, buf_size); // Initialize the buffer to avoid garbage values
    memset(buffer, 'A', 10); // Write 'A' to the first 10 bytes
    memset(buffer + buf_size - 10, 'A', 10); // Write 'A' to the last 10 bytes

    return buffer; // Return the allocated buffer
}