
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

/**
Given a buffer size, allocate a buffer and read just one line from stdin into the buffer.

@param buf_size: the size of the buffer
@return the buffer containing the line read from stdin, or NULL if an error occurs
*/
char* read_stdin_to_buffer(int buf_size) {
    // Validate the buffer size to ensure it is reasonable
    if (buf_size <= 0 || buf_size > SIZE_MAX) {
        fprintf(stderr, "Invalid buffer size: %d\n", buf_size);
        return NULL;
    }

    // Allocate memory for the buffer
    char* buf = (char*)malloc((size_t)buf_size);
    if (buf == NULL) {
        fprintf(stderr, "Memory allocation failed: %s\n", strerror(errno));
        return NULL;
    }

    // Clear the buffer to ensure it is initialized
    memset(buf, 0, (size_t)buf_size);

    // Read a line from stdin into the buffer
    if (fgets(buf, buf_size, stdin) == NULL) {
        if (feof(stdin)) {
            fprintf(stderr, "End of input reached.\n");
        } else {
            fprintf(stderr, "Error reading from stdin: %s\n", strerror(errno));
        }
        free(buf);
        return NULL;
    }

    // Ensure the buffer is null-terminated
    buf[buf_size - 1] = '\0';

    return buf;
}