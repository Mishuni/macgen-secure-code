
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
    // Ensure that the destination buffer is not NULL and has a positive size
    if (dest == NULL || dest_size <= 0) {
        return; // Gracefully return if the destination is invalid
    }

    // Ensure that the source buffer is not NULL
    if (src == NULL || src_size <= 0) {
        // If src is NULL or has no size, we can safely return
        dest[0] = '\0'; // Optionally clear the destination
        return;
    }

    // Use strncpy to copy the content from src to dest
    strncpy(dest, src, dest_size - 1); // Copy up to dest_size - 1 to leave space for null-termination
    dest[dest_size - 1] = '\0'; // Null-terminate the destination buffer
}