
#include <stdio.h>
#include <string.h>

/**
use strncpy to copy the content of src to dest as much as possible

@param dest: the destination buffer
@param dest_size: the size of the destination buffer
@param src: the source buffer
@param src_size: the size of the source buffer
*/
void copy_to_dest(char* dest, int dest_size, char* src, int src_size) {
    if (dest == NULL || src == NULL || dest_size <= 0 || src_size <= 0) {
        return; // Handle invalid input
    }

    // Calculate the number of characters to copy
    int num_to_copy = (src_size < dest_size - 1) ? src_size : dest_size - 1;

    // Use strncpy to copy the content and ensure null-termination
    strncpy(dest, src, num_to_copy);
    dest[num_to_copy] = '\0'; // Ensure null-termination
}