
#include <stdio.h>
#include <stdlib.h>

char* read_stdin_to_buffer(int buf_size) {
    if (buf_size <= 0) {
        return NULL;
    }

    char* buf = (char*)malloc(buf_size);
    if (buf == NULL) {
        return NULL;
    }

    if (fgets(buf, buf_size, stdin) == NULL) {
        free(buf);
        return NULL;
    }

    // Ensure the buffer is null-terminated
    buf[buf_size - 1] = '\0';

    // Check if the input was truncated
    size_t len = 0;
    while (len < buf_size && buf[len] != '\0' && buf[len] != '\n') {
        len++;
    }

    if (len == buf_size - 1 && buf[len] != '\n') {
        // Input was truncated, handle accordingly
        free(buf);
        return NULL;
    }

    return buf;
}