
#include <stdio.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>

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

    // Ensure the buffer has enough space for the prefix
    const int prefix_length = 14;
    if (BUF_SIZE <= prefix_length) {
        fprintf(stderr, "Buffer size is too small for the prefix.\n");
        close(fd);
        return;
    }

    // Read file content to buf at offset 14
    int remaining = BUF_SIZE - prefix_length;
    int count = read(fd, buf + prefix_length, remaining);
    if (count < 0) {
        perror("Error reading file");
        close(fd);
        return;
    }

    // Close the file descriptor to prevent resource leakage
    if (close(fd) < 0) {
        perror("Error closing file");
        return;
    }

    // Copy all content in buf to out
    memcpy(out, buf, prefix_length + count);
}