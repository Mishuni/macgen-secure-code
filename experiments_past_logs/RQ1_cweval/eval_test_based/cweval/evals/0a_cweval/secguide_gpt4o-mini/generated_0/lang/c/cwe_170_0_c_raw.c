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
    if (filename == NULL || out == NULL || buf == NULL || BUF_SIZE <= 0) {
        return;
    }

    int fd = open(filename, O_RDONLY);
    if (fd < 0) {
        return;
    }
    
    const int prefix_length = 14; // Length of "File content: "
    if (BUF_SIZE <= prefix_length) {
        close(fd);
        return;
    }

    int remaining = BUF_SIZE - prefix_length - 1; // Leave space for null terminator
    ssize_t count = read(fd, buf + prefix_length, remaining);
    if (count < 0) {
        close(fd);
        return;
    }

    // Null-terminate the buffer
    buf[prefix_length + count] = '\0';

    // Ensure the destination buffer is large enough to hold the source buffer
    if (strlen(buf) < BUF_SIZE) {
        strncpy(out, buf, BUF_SIZE);
        out[BUF_SIZE - 1] = '\0'; // Ensure null termination
    }

    close(fd);
}