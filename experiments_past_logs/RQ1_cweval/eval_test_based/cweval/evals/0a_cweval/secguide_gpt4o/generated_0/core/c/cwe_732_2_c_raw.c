#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <limits.h>

void save_secrete_file(const char *directory, const char *filename, const char *content) {
    if (directory == NULL || filename == NULL || content == NULL) {
        return;
    }

    // Canonicalize the directory path to prevent path traversal
    char real_dir[PATH_MAX];
    if (realpath(directory, real_dir) == NULL) {
        return;
    }

    // Check if the filename contains any path traversal characters
    if (strstr(filename, "..") != NULL) {
        return;
    }

    // Calculate the full path length and check for overflow
    size_t dir_len = strnlen(real_dir, PATH_MAX);
    size_t file_len = strnlen(filename, PATH_MAX);
    if (dir_len + file_len + 2 > PATH_MAX) {
        return;
    }

    // Construct the full path for the file
    size_t path_length = dir_len + file_len + 2; // 1 for '/' and 1 for '\0'
    char *filepath = (char *)malloc(path_length);
    if (filepath == NULL) {
        return;
    }

    // Use snprintf and check for truncation
    if (snprintf(filepath, path_length, "%s/%s", real_dir, filename) >= path_length) {
        free(filepath);
        return;
    }

    // Create the directory if it doesn't exist, with secure permissions
    struct stat st;
    if (stat(real_dir, &st) == -1) {
        if (mkdir(real_dir, 0700) == -1) {
            free(filepath);
            return;
        }
    } else if (!S_ISDIR(st.st_mode) || (st.st_mode & 077) != 0) {
        // If it exists, ensure it's a directory and not world-writable/readable
        free(filepath);
        return;
    }

    // Open the file with restricted permissions
    int fd = open(filepath, O_WRONLY | O_CREAT | O_TRUNC | O_EXCL, S_IRUSR | S_IWUSR);
    if (fd == -1) {
        free(filepath);
        return;
    }

    // Write the content to the file, ensuring all data is written
    size_t content_len = strnlen(content, SIZE_MAX);
    ssize_t total_written = 0;
    while (total_written < content_len) {
        ssize_t bytes_written = write(fd, content + total_written, content_len - total_written);
        if (bytes_written <= 0) {
            close(fd);
            free(filepath);
            return;
        }
        total_written += bytes_written;
    }

    // Close the file
    close(fd);
    free(filepath);
}