
#include <stdio.h>
#include <string.h>

void copy_to_dest(char* dest, int dest_size, char* src, int src_size) {
    if (dest == NULL || src == NULL || dest_size <= 0) {
        return; // Handle null pointers and invalid sizes
    }

    // Calculate the number of bytes to copy
    int bytes_to_copy = (src_size < dest_size - 1) ? src_size : dest_size - 1;

    // Perform the copy operation
    strncpy(dest, src, bytes_to_copy);

    // Ensure null-termination
    dest[bytes_to_copy] = '\0';
}