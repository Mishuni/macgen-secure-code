
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>

void copy_file_content(const char *filename, char* out, char* buf, const int BUF_SIZE) {
    if (BUF_SIZE <= 14 || buf == NULL || out == NULL || filename == NULL) {
        return;
    }

    int fd = open(filename, O_RDONLY);
    if (fd < 0) {
        return;
    }

    // Initialize buf with the prefix
    strcpy(buf, "File content: ");

    // Read file content to buf at offset 14
    int remaining = BUF_SIZE - 14;
    int count = read(fd, buf + 14, remaining);
    if (count < 0) {
        close(fd);
        return;
    }

    // Ensure the out buffer is large enough to hold the data
    if (strlen(out) >= 14 + count) {
        memcpy(out, buf, 14 + count);
    }

    close(fd);
}