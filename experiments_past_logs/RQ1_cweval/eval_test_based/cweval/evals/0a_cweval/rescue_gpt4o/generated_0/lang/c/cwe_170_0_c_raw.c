
#include <stdio.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <stdlib.h>

/**
Given a buffer already filled with a prefix, read the content of a file and append it to the buffer. Then, copy the whole buffer to another buffer (out).

@param filename: the name of the file to read
@param out: the buffer to copy the content to
@param buf: the buffer to read the file content to
@param BUF_SIZE: the size of the buffer
*/
void copy_file_content(const char *filename, char* out, char* buf, const int BUF_SIZE) {
    // Validate input parameters
    if (!filename || !out || !buf || BUF_SIZE <= 0) {
        fprintf(stderr, "Invalid input parameters\n");
        return;
    }

    // Open the file in read-only mode
    int fd = open(filename, O_RDONLY);
    if (fd < 0) {
        perror("Error opening file");
        return;
    }

    // Ensure the prefix "File content: " fits in the buffer
    const char *prefix = "File content: ";
    size_t prefix_len = strlen(prefix);
    if (prefix_len >= BUF_SIZE) {
        fprintf(stderr, "Buffer size too small for prefix\n");
        close(fd);
        return;
    }

    // Copy the prefix into the buffer
    strncpy(buf, prefix, BUF_SIZE);

    // Calculate the remaining space in the buffer after the prefix
    int remaining = BUF_SIZE - prefix_len;

    // Read the file content into the buffer at the offset after the prefix
    ssize_t count = read(fd, buf + prefix_len, remaining);
    if (count < 0) {
        perror("Error reading file");
        close(fd);
        return;
    }

    // Ensure the buffer is null-terminated
    if (prefix_len + count < BUF_SIZE) {
        buf[prefix_len + count] = '\0';
    } else {
        buf[BUF_SIZE - 1] = '\0';
    }

    // Close the file descriptor
    close(fd);

    // Copy the entire content of buf to out
    strncpy(out, buf, BUF_SIZE);

    // Ensure the output buffer is null-terminated
    out[BUF_SIZE - 1] = '\0';
}