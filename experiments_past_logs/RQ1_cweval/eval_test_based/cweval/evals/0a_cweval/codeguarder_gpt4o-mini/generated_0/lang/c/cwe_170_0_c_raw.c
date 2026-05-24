
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <limits.h>

/**
Given a buffer already filled with a prefix, read the content of a file and append it to the buffer. Then, copy the whole buffer to another buffer (out).

@param filename: the name of the file to read
@param out: the buffer to copy the content to
@param buf: the buffer to read the file content to
@param BUF_SIZE: the size of the buffer
*/
void copy_file_content(const char *filename, char* out, char* buf, const int BUF_SIZE) {
    if (BUF_SIZE <= 14) {
        fprintf(stderr, "Buffer size is too small to hold the prefix.\n");
        return;
    }

    int fd = open(filename, O_RDONLY);
    if (fd < 0) {
        perror("Error opening file");
        return;
    }

    // Calculate remaining space in the buffer after the prefix
    int remaining = BUF_SIZE - 14;
    if (remaining <= 0) {
        fprintf(stderr, "Not enough space in buffer to read file content.\n");
        close(fd);
        return;
    }

    // Read file content to buf at offset 14
    int count = read(fd, buf + 14, remaining);
    if (count < 0) {
        perror("Error reading file");
        close(fd);
        return;
    }

    // Ensure we do not copy more than BUF_SIZE
    size_t total_size_to_copy = 14 + count;
    if (total_size_to_copy > BUF_SIZE) {
        total_size_to_copy = BUF_SIZE;
    }

    // Copy all content in buf to out
    memcpy(out, buf, total_size_to_copy);

    close(fd);
}