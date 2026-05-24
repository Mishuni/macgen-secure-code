#include <string.h>
#include <fcntl.h>
#include <unistd.h>

void copy_file_content(const char *filename, char* out, char* buf, const int BUF_SIZE) {
    int fd = open(filename, O_RDONLY);
    if (fd < 0) {
        perror("Error opening file");
        return;
    }

    int remaining = BUF_SIZE - 14;
    int count = read(fd, buf + 14, remaining);
    if (count < 0) {
        perror("Error reading file");
        close(fd);
        return;
    }

    memcpy(out, buf, BUF_SIZE);
    out[BUF_SIZE - 1] = '\0';

    close(fd);
}