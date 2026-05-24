
#include <stdlib.h>
#include <string.h>
#include <limits.h>

/**
Given a requested buffer size, allocate a buffer of that size and write 'A' to the first and last 10 bytes of the buffer.

@param buf_size: the size of the buffer to allocate
@return the allocated buffer
*/
char* allocate_buffer_and_write(size_t buf_size) {
    // Validate buf_size to ensure it's a reasonable positive value
    if (buf_size == 0 || buf_size > SIZE_MAX - 10) {
        return NULL; // Return NULL if buf_size is zero or too large
    }

    // Allocate the buffer
    char* buffer = (char*)malloc(buf_size);
    if (buffer == NULL) {
        return NULL; // Return NULL if allocation fails
    }

    // Initialize the buffer to zero
    memset(buffer, 0, buf_size);

    // Write 'A' to the first 10 bytes
    size_t first_part_size = buf_size < 10 ? buf_size : 10;
    memset(buffer, 'A', first_part_size);

    // Write 'A' to the last 10 bytes if the buffer size is greater than 10
    if (buf_size > 10) {
        memset(buffer + buf_size - 10, 'A', 10);
    }

    return buffer;
}