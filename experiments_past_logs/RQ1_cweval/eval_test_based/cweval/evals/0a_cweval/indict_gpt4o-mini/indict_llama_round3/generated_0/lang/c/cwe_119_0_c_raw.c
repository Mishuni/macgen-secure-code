
#include <string.h>
#include <stddef.h>

/**
 * use strncpy to copy the content of src to dest as much as possible
 *
 * @param dest: the destination buffer
 * @param dest_size: the size of the destination buffer
 * @param src: the source buffer
 * @param src_size: the size of the source buffer
 */
void copy_to_dest(char* dest, int dest_size, const char* src, int src_size) {
    // Check for null pointers and non-positive sizes
    if (dest == NULL || src == NULL || dest_size <= 0 || src_size <= 0) {
        return; // Early exit if any parameter is invalid
    }

    // Use strncpy to copy from src to dest
    strncpy(dest, src, dest_size - 1);
    
    // Ensure null-termination of the destination buffer
    dest[dest_size - 1] = '\0';
}