#include <string.h>

void copy_to_dest(char* dest, int dest_size, char* src, int src_size) {
    if (dest_size <= 0) return;
    int num_to_copy = (src_size < dest_size - 1) ? src_size : dest_size - 1;
    strncpy(dest, src, num_to_copy);
    dest[num_to_copy] = '\0';
}