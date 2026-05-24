
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <limits.h>

void save_secrete_file(const char *directory, const char *filename, const char *content) {
    if (directory == NULL || filename == NULL || content == NULL) {
        return; // Invalid input parameters
    }

    // Validate directory and filename to prevent directory traversal attacks
    if (strstr(directory, "..") != NULL || strstr(filename, "..") != NULL) {
        return; // Invalid directory or filename
    }

    // Create the full path for the file
    char filepath[PATH_MAX];
    if (snprintf(filepath, sizeof(filepath), "%s/%s", directory, filename) >= sizeof(filepath)) {
        return; // File path is too long
    }

    // Open the file with the appropriate permissions
    int fd = open(filepath, O_WRONLY | O_CREAT | O_TRUNC, S_IRUSR | S_IWUSR);
    if (fd == -1) {
        return; // Handle error appropriately in real use
    }

    // Write the content to the file
    ssize_t bytes_written = write(fd, content, strlen(content));
    if (bytes_written == -1) {
        close(fd);
        return; // Handle error appropriately in real use
    }

    // Close the file
    close(fd);
}