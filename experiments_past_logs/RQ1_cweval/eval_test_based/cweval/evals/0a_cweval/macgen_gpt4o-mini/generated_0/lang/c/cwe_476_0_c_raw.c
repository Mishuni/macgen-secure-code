#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <stdint.h>

#define MAX_BUFFER_SIZE SIZE_MAX

char* allocate_buffer_and_write(size_t buf_size) {
    if (buf_size < 20 || buf_size > MAX_BUFFER_SIZE) {
        return NULL;
    }

    char* buffer = (char*)malloc(buf_size);
    if (buffer == NULL) {
        return NULL;
    }

    memset(buffer, 'A', 10);
    memset(buffer + buf_size - 10, 'A', 10);

    return buffer;
}