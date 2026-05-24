
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

char* read_stdin_to_buffer(int buf_size) {
    if (buf_size <= 0) {
        return NULL; // Invalid buffer size
    }

    char* buf = (char*)malloc(buf_size);
    if (!buf) {
        perror("Failed to allocate memory");
        return NULL; // Memory allocation failed
    }

    // Read a line from stdin, ensuring we do not exceed the buffer size
    if (fgets(buf, buf_size, stdin) == NULL) {
        free(buf); // Free allocated memory on failure
        return NULL; // Reading failed
    }

    // Ensure the buffer is null-terminated (fgets does this automatically)
    return buf;
}