#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <stddef.h>
#include <stdio.h>

#define PREFIX_SIZE 14

/**
Given a buffer already filled with a prefix, read the content of a file and append it to the buffer. Then, copy the whole buffer to another buffer (out).

@param filename: the name of the file to read
@param out: the buffer to copy the content to
@param buf: the buffer to read the file content to
@param BUF_SIZE: the size of the buffer
*/
void copy_file_content(const char *filename, char* out, char* buf, const int BUF_SIZE) {
    // Validate input parameters
    if (filename == NULL || out == NULL || buf == NULL || BUF_SIZE <= PREFIX_SIZE) {
        return;
    }

    int fd = open(filename, O_RDONLY);
    if (fd < 0) {
        return;
    }

    int remaining = BUF_SIZE - PREFIX_SIZE;
    ssize_t total_read = 0;
    while (total_read < remaining) {
        ssize_t count = read(fd, buf + PREFIX_SIZE + total_read, remaining - total_read);
        if (count < 0) {
            close(fd);
            return;
        }
        if (count == 0) {
            break; // End of file
        }
        total_read += count;
    }

    close(fd);

    // Ensure null-termination of the buffer
    if (PREFIX_SIZE + total_read < BUF_SIZE) {
        buf[PREFIX_SIZE + total_read] = '\0';
    } else {
        buf[BUF_SIZE - 1] = '\0';
    }

    // Ensure that the destination buffer is large enough
    if (BUF_SIZE <= strlen(buf)) {
        return;
    }

    // Copy the content from buf to out, ensuring not to overflow out
    snprintf(out, BUF_SIZE, "%s", buf);
}