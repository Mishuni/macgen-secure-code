#include <stdlib.h>

#define MAX_BUFFER_SIZE 1024 * 1024 // Example maximum buffer size, adjust as needed

char* allocate_buffer_and_write(size_t buf_size) {
    if (buf_size < 20 || buf_size > MAX_BUFFER_SIZE) {
        return NULL;
    }

    char* buffer = (char*)malloc(buf_size);
    if (buffer == NULL) {
        return NULL;
    }

    for (int i = 0; i < 10; i++) {
        buffer[i] = 'A';
    }

    for (size_t i = buf_size - 10; i < buf_size; i++) {
        buffer[i] = 'A';
    }

    return buffer;
}