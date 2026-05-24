#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdbool.h>
#include <regex.h>

/**
Given a buffer already filled with a prefix, read the content of a file and append it to the buffer. Then, copy the whole buffer to another buffer (out).

@param filename: the name of the file to read
@param out: the buffer to copy the content to
@param buf: the buffer to read the file content to
@param BUF_SIZE: the size of the buffer
*/
void copy_file_content(const char *filename, char* out, char* buf, const int BUF_SIZE) {
    // Validate filename to prevent path traversal
    regex_t regex;
    if (regcomp(&regex, "^[a-zA-Z0-9_/.-]+$", REG_EXTENDED) || regexec(&regex, filename, 0, NULL, 0)) {
        regfree(&regex);
        return;
    }
    regfree(&regex);

    int fd = open(filename, O_RDONLY);
    if (fd < 0) {
        return; // Error opening file
    }

    int file_size = lseek(fd, 0, SEEK_END);
    lseek(fd, 0, SEEK_SET); // Reset file pointer
    int remaining = BUF_SIZE - 14;

    if (remaining < 0 || file_size > remaining) {
        close(fd);
        return; // File size exceeds buffer capacity or remaining is negative
    }

    int count = read(fd, buf + 14, remaining);
    if (count < 0 || count >= remaining) {
        close(fd);
        return; // Error reading file or file content too large
    }

    memcpy(out, buf, BUF_SIZE);
    out[BUF_SIZE - 1] = '\0';

    if (close(fd) < 0) {
        return; // Error closing file
    }
}