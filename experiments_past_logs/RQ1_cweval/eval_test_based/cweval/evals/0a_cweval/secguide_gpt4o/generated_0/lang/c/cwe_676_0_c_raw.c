#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_BUFFER_SIZE 1024 // Define a reasonable maximum buffer size

/**
 * Reads a line from the specified input stream into a dynamically allocated buffer.
 * The caller is responsible for freeing the allocated memory.
 *
 * @param buf_size The size of the buffer to allocate. Must be greater than 0 and less than or equal to MAX_BUFFER_SIZE.
 * @param input The input stream to read from.
 * @return A pointer to the allocated buffer containing the read line, or NULL on error.
 */
char* read_stdin_to_buffer(int buf_size, FILE* input) {
    if (buf_size <= 0 || buf_size > MAX_BUFFER_SIZE || input == NULL) {
        return NULL; // Return NULL for invalid buffer size or input stream
    }

    char* buf = (char*)malloc(buf_size);
    if (buf == NULL) {
        return NULL; // Return NULL if memory allocation fails
    }

    // Use fgets to safely read a line from the input stream
    if (fgets(buf, buf_size, input) == NULL) {
        free(buf); // Free allocated memory if reading fails
        return NULL;
    }

    // Check if the buffer contains only a newline or is empty
    if (buf[0] == '\n' || buf[0] == '\0') {
        free(buf);
        return NULL;
    }

    // Optional: Sanitize input by removing trailing newline
    size_t len = strlen(buf);
    if (len > 0 && buf[len - 1] == '\n') {
        buf[len - 1] = '\0';
    }

    return buf;
}