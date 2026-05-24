
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINE_LENGTH 1024

/**
Given a buffer size, allocate a buffer and read just one line from stdin into the buffer.

@param buf_size: the size of the buffer
@return the buffer containing the line read from stdin
*/
char* read_stdin_to_buffer(int buf_size) {
    if (buf_size <= 0 || buf_size > MAX_LINE_LENGTH) {
        return NULL; // Invalid buffer size
    }

    char* buf = (char*)malloc(buf_size);
    if (!buf) {
        return NULL; // Memory allocation failed
    }

    if (fgets(buf, buf_size, stdin) == NULL) {
        free(buf);
        return NULL; // Reading from stdin failed
    }

    // Ensure null-termination
    buf[buf_size - 1] = '\0';

    return buf;
}