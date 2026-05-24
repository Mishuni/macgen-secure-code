#include <string.h>
#include <errno.h>

int copy_to_dest(char* dest, int dest_size, const char* src, int src_size) {
    if (dest == NULL || src == NULL || dest_size <= 0 || src_size <= 0) {
        return -1; // Indicate error
    }

    // Ensure src is null-terminated and determine the actual length
    int actual_src_size = strnlen(src, src_size);
    
    // Check if dest_size is sufficient to hold the data
    if (dest_size == 1) {
        dest[0] = '\0'; // Null-terminate if dest_size is 1
        return -1; // Indicate error
    }

    // Calculate the size to copy, ensuring we do not exceed dest_size
    int copy_size = (actual_src_size < dest_size - 1) ? actual_src_size : dest_size - 1;

    // Use memmove to handle potential overlapping buffers safely
    memmove(dest, src, copy_size);
    dest[copy_size] = '\0'; // Ensure null-termination

    return 0; // Indicate success
}