#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_BUFFER_SIZE 1024

char* read_stdin_to_buffer(int buf_size) {
    if (buf_size <= 0 || buf_size > MAX_BUFFER_SIZE) {
        return NULL;
    }

    char* buf = (char*)malloc(buf_size);
    if (buf == NULL) {
        return NULL;
    }

    if (fgets(buf, buf_size, stdin)) {
        char *p = strchr(buf, '\n');
        if (p) {
            *p = '\0';
        }
    } else {
        free(buf);
        return NULL;
    }

    return buf;
}