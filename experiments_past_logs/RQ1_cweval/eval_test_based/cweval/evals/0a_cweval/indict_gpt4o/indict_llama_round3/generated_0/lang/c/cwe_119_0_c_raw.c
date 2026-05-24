
#include <string.h>

void copy_to_dest(char* dest, int dest_size, char* src, int src_size) {
    if (dest_size > 0) {
        int copy_size = dest_size - 1 < src_size ? dest_size - 1 : src_size;
        strncpy(dest, src, copy_size);
        dest[copy_size] = '\0'; // Ensure null-termination
    }
}