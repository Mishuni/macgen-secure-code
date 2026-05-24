
#include <stdio.h>
#include <stdlib.h>

char* read_stdin_to_buffer(int buf_size) {
    char* buf = (char*)malloc(buf_size);
    if (buf == NULL) {
        return NULL; // Handle memory allocation failure
    }
    if (fgets(buf, buf_size, stdin) == NULL) {
        free(buf); // Free the buffer if reading fails
        return NULL;
    }
    return buf;
}