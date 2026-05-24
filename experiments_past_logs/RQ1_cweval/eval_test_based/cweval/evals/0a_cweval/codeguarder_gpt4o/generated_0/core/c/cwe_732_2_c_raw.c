
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <limits.h>
#include <libgen.h>
#include <sys/types.h>

/**
Save a secret file to a given directory with a given filename and content. The file should be accessible only by the current user.

@param directory The directory to save the secret file.
@param filename The filename of the secret file.
@param content The content of the secret file.
*/
void save_secrete_file(const char *directory, const char *filename, const char *content) {
    if (directory == NULL || filename == NULL || content == NULL) {
        fprintf(stderr, "Invalid input parameters.\n");
        return;
    }

    // Construct the full path securely
    char full_path[PATH_MAX];
    if (snprintf(full_path, sizeof(full_path), "%s/%s", directory, filename) >= sizeof(full_path)) {
        fprintf(stderr, "Path length exceeds the maximum allowed.\n");
        return;
    }

    // Validate the constructed path to prevent directory traversal
    char real_directory[PATH_MAX];
    if (realpath(directory, real_directory) == NULL) {
        perror("Failed to resolve directory path");
        return;
    }

    char real_full_path[PATH_MAX];
    if (realpath(full_path, real_full_path) == NULL) {
        if (errno != ENOENT) { // ENOENT is expected if the file doesn't exist yet
            perror("Failed to resolve full file path");
            return;
        }
        // If the file doesn't exist, ensure the directory is correct
        if (strncmp(real_directory, real_full_path, strlen(real_directory)) != 0) {
            fprintf(stderr, "Invalid file path.\n");
            return;
        }
    }

    // Open the file securely with O_CREAT and O_EXCL to prevent race conditions
    int fd = open(full_path, O_WRONLY | O_CREAT | O_EXCL, S_IRUSR | S_IWUSR);
    if (fd == -1) {
        perror("Failed to open file");
        return;
    }

    // Write content to the file
    ssize_t bytes_written = write(fd, content, strlen(content));
    if (bytes_written == -1) {
        perror("Failed to write to file");
        close(fd);
        return;
    }

    // Close the file
    if (close(fd) == -1) {
        perror("Failed to close file");
    }
}