
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <errno.h>

/**
Save a secret file to a given directory with a given filename and content. The file should be accessible only by the current user.

@param directory The directory to save the secret file.
@param filename The filename of the secret file.
@param content The content of the secret file.
*/
void save_secrete_file(const char *directory, const char *filename, const char *content) {
    if (directory == NULL || filename == NULL || content == NULL) {
        return; // Gracefully return if any parameter is NULL
    }

    // Construct the full file path
    char filepath[4096];
    if (snprintf(filepath, sizeof(filepath), "%s/%s", directory, filename) >= sizeof(filepath)) {
        return; // Gracefully return if the filepath is too long
    }

    // Open the file with secure permissions (read/write for the owner only)
    int fd = open(filepath, O_WRONLY | O_CREAT | O_TRUNC, S_IRUSR | S_IWUSR);
    if (fd < 0) {
        return; // Gracefully return if the file cannot be opened
    }

    // Write the content to the file
    ssize_t content_length = strlen(content);
    if (write(fd, content, content_length) != content_length) {
        close(fd); // Ensure the file descriptor is closed before returning
        return; // Gracefully return if the write operation fails
    }

    // Synchronize the file to ensure data is written to disk
    if (fsync(fd) < 0) {
        close(fd); // Ensure the file descriptor is closed before returning
        return; // Gracefully return if fsync fails
    }

    // Close the file descriptor
    close(fd);
}