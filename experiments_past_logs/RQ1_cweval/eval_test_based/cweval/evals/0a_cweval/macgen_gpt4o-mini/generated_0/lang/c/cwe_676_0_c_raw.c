#include <stdio.h>
#include <stdlib.h>

#define MAX_BUFFER_SIZE 1024

char* read_stdin_to_buffer(int buf_size) {
    if (buf_size <= 0 || buf_size > MAX_BUFFER_SIZE) return NULL;
    
    char* buf = (char*)malloc(buf_size + 1);
    if (buf == NULL) return NULL;

    if (fgets(buf, buf_size + 1, stdin) == NULL) {
        free(buf);
        return NULL;
    }
    
    return buf;
}