
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

char* read_stdin_to_buffer(int buf_size) {
    // Validate buf_size to prevent buffer overflow and negative sizes
    if (buf_size <= 0 || buf_size > INT_MAX) {
        return NULL; // Invalid buffer size
    }

    char* buf = (char*)malloc(buf_size);
    if (buf == NULL) {
        return NULL; // Handle memory allocation failure
    }

    // Read a line from stdin into the buffer
    if (fgets(buf, buf_size, stdin) == NULL) {
        free(buf); // Free the buffer if reading fails
        return NULL;
    }

    // Check if the input was truncated
    if (buf[buf_size - 1] != '\0' && buf[buf_size - 1] != '\n') {
        // Clear the input buffer if the line was too long
        int c;
        while ((c = getchar()) != '\n' && c != EOF);
    }

    // Ensure the buffer is null-terminated
    buf[buf_size - 1] = '\0';

    return buf;
}