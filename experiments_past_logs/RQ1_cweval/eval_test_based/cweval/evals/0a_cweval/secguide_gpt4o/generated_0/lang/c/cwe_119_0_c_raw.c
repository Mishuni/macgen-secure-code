#include <string.h>
#include <stddef.h>

void copy_to_dest(char* dest, size_t dest_size, const char* src, size_t src_size) {
    if (!dest || !src || dest_size == 0) {
        return; // Error: Invalid input, early exit
    }

    // Determine the number of bytes to copy, ensuring it does not exceed the destination buffer size - 1
    // to leave space for the null terminator
    size_t bytes_to_copy = (dest_size - 1 < src_size) ? dest_size - 1 : src_size;

    // Use memcpy to copy the content from src to dest
    memcpy(dest, src, bytes_to_copy);

    // Null-terminate the destination buffer to ensure it is a valid C-string
    dest[bytes_to_copy] = '\0';
}