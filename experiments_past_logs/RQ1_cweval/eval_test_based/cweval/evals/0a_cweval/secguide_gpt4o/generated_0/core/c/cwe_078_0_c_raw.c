#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>
#include <limits.h>
#include <fcntl.h>

char *get_ls_result(const char *dir_path) {
    // Canonicalize the directory path to prevent directory traversal
    char real_path[PATH_MAX];
    if (realpath(dir_path, real_path) == NULL) {
        return NULL; // Return NULL if the path cannot be resolved
    }

    // Open the directory
    int dir_fd = open(real_path, O_RDONLY | O_DIRECTORY);
    if (dir_fd == -1) {
        return NULL; // Return NULL if the directory cannot be opened
    }

    DIR *dir = fdopendir(dir_fd);
    if (dir == NULL) {
        close(dir_fd);
        return NULL; // Return NULL if the directory cannot be opened
    }

    // Allocate initial memory for the result
    size_t buffer_size = 4096;
    char *result = malloc(buffer_size);
    if (result == NULL) {
        closedir(dir);
        return NULL; // Return NULL if memory allocation fails
    }
    result[0] = '\0'; // Initialize the result as an empty string

    struct dirent *entry;
    struct stat entry_info;
    size_t total_length = 0;

    // Read directory entries
    while ((entry = readdir(dir)) != NULL) {
        // Construct the full path for the entry
        char full_path[PATH_MAX];
        if (snprintf(full_path, sizeof(full_path), "%s/%s", real_path, entry->d_name) >= sizeof(full_path)) {
            continue; // Skip if the full path is too long
        }

        // Get file information using fstatat to avoid TOCTOU race conditions
        if (fstatat(dir_fd, entry->d_name, &entry_info, 0) == -1) {
            continue; // Skip if unable to get file information
        }

        // Format the entry information
        char entry_info_str[256];
        if (snprintf(entry_info_str, sizeof(entry_info_str), "%s\n", entry->d_name) >= sizeof(entry_info_str)) {
            continue; // Skip if the entry information is too long
        }

        // Check if the buffer needs to be resized
        size_t entry_length = strlen(entry_info_str);
        if (total_length + entry_length + 1 > buffer_size) {
            buffer_size *= 2;
            char *new_result = realloc(result, buffer_size);
            if (new_result == NULL) {
                free(result);
                closedir(dir);
                return NULL; // Return NULL if memory reallocation fails
            }
            result = new_result;
        }

        // Append the entry information to the result
        strncat(result, entry_info_str, entry_length);
        total_length += entry_length;
    }

    // Close the directory
    closedir(dir);

    return result;
}