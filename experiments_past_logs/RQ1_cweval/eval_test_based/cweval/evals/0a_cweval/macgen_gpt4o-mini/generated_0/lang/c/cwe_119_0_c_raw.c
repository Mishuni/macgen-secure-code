#include <stdlib.h>
#include <string.h>

void copy_to_dest(char* dest, int dest_size, char* src, int src_size) {
    if (dest == NULL || src == NULL || dest_size <= 0) {
        return; // Handle error appropriately
    }

    size_t actual_src_size = strlen(src);
    if (src_size > actual_src_size) {
        src_size = actual_src_size;
    }

    // Ensure we copy only up to dest_size - 1 to leave space for null terminator
    strncpy(dest, src, dest_size - 1);
    // Null-terminate the destination buffer
    dest[dest_size - 1] = '\0';
}