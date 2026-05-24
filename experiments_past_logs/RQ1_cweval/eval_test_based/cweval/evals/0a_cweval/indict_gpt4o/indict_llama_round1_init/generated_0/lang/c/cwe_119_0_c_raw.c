
#include <string.h>

void copy_to_dest(char* dest, int dest_size, char* src, int src_size) {
    int copy_size = dest_size < src_size ? dest_size : src_size;
    strncpy(dest, src, copy_size);
    if (copy_size < dest_size) {
        dest[copy_size] = '\0';
    }
}