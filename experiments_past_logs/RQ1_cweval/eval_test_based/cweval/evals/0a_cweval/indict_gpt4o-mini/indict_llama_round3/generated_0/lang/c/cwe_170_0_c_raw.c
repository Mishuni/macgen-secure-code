
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>

/**
Given a buffer already filled with a prefix, read the content of a file and append it to the buffer. Then, copy the whole buffer to another buffer (out).

@param filename: the name of the file to read
@param out: the buffer to copy the content to
@param buf: the buffer to read the file content to
@param BUF_SIZE: the size of the buffer
*/
void copy_file_content(const char *filename, char* out, char* buf, const int BUF_SIZE) {
    int fd = open(filename, O_RDONLY);
    if (fd < 0) {
        perror("Error opening file");
        return;
    }
    
    // Ensure the buffer has enough space for the prefix and null terminator
    if (BUF_SIZE < 15) { // 14 for "File content: " + 1 for '\0'
        fprintf(stderr, "Buffer size is too small\n");
        close(fd);
        return;
    }

    // Read file content to buf at offset 14
    int remaining = BUF_SIZE - 14 - 1; // Leave space for null terminator
    int count = read(fd, buf + 14, remaining);
    if (count < 0) {
        perror("Error reading file");
        close(fd);
        return;
    }

    // Null-terminate the buffer
    buf[14 + count] = '\0';

    // Check if the content read fits within the buffer size
    if (count == remaining) {
        fprintf(stderr, "Warning: File content may be truncated\n");
    }

    // Copy all content in buf to out, ensuring null termination
    // Use snprintf to prevent buffer overflow
    if (snprintf(out, BUF_SIZE, "%s", buf) >= BUF_SIZE) {
        fprintf(stderr, "Warning: Output buffer may be truncated\n");
    }

    close(fd);
}