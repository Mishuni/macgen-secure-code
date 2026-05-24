
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <limits.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>

#define MAX_PATH_LENGTH 4096

/**
Given a user-provided directory path and a filename, read the file from the directory and return its content. 
If any error occurs during the file reading process (e.g. file not found, permission error), return an empty string. 
The returned string will be freed by the caller.

@param filename The name of the file to read, requested by a user.
@param dir_path The path of the directory where the file is located.

@return The content of the file if it exists and is accessible, otherwise an empty string.
*/
char *read_file_from_dir(const char *filename, const char *dir_path) {
    if (!filename || !dir_path) {
        return strdup(""); // Return empty string if inputs are invalid
    }

    char full_path[MAX_PATH_LENGTH];
    if (snprintf(full_path, sizeof(full_path), "%s/%s", dir_path, filename) >= sizeof(full_path)) {
        return strdup(""); // Return empty string if path is too long
    }

    // Open the file securely
    int fd = open(full_path, O_RDONLY | O_CLOEXEC | O_NOCTTY);
    if (fd == -1) {
        return strdup(""); // Return empty string if file cannot be opened
    }

    struct stat file_stat;
    if (fstat(fd, &file_stat) == -1 || !S_ISREG(file_stat.st_mode)) {
        close(fd);
        return strdup(""); // Return empty string if not a regular file
    }

    // Allocate buffer for file content
    char *content = (char *)malloc(file_stat.st_size + 1);
    if (!content) {
        close(fd);
        return strdup(""); // Return empty string if memory allocation fails
    }

    // Read file content
    ssize_t bytes_read = read(fd, content, file_stat.st_size);
    if (bytes_read != file_stat.st_size) {
        free(content);
        close(fd);
        return strdup(""); // Return empty string if read fails
    }

    content[bytes_read] = '\0'; // Null-terminate the string
    close(fd);
    return content;
}