#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char* read_stdin_to_buffer(int buf_size) {
    if (buf_size <= 0 || buf_size > 1024) { // Limit to a reasonable maximum size
        return NULL;
    }

    char* buf = malloc(buf_size);
    if (buf == NULL) {
        return NULL; // Memory allocation failed
    }

    if (fgets(buf, buf_size, stdin) == NULL) {
        free(buf);
        return NULL; // Input reading failed
    }

    // Remove newline character if present
    size_t len = strlen(buf);
    if (len > 0 && buf[len - 1] == '\n') {
        buf[len - 1] = '\0';
    }

    // Additional input validation can be added here
    // For example, check for specific formats or disallowed characters

    return buf; // Caller is responsible for freeing the memory
}