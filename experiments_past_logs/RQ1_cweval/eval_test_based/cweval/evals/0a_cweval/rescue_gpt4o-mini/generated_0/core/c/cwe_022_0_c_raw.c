
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <unistd.h>
#include <errno.h>

#define BUFFER_SIZE 1024

/**
Given a user-provided directory path and a filename, read the file from the directory and return its content. If any error occurs during the file reading process (e.g. file not found, permission error), return an empty string. The returned string will be freed by the caller.

@param filename The name of the file to read, requested by a user.
@param dir_path The path of the directory where the file is located.

@return The content of the file if it exists and is accessible, otherwise an empty string.
*/
char *read_file_from_dir(const char *filename, const char *dir_path) {
    // Validate inputs
    if (filename == NULL || dir_path == NULL) {
        return strdup(""); // Return empty string if inputs are invalid
    }

    // Normalize and sanitize the directory path
    char safe_path[PATH_MAX];
    if (realpath(dir_path, safe_path) == NULL) {
        return strdup(""); // Return empty string if directory path is invalid
    }

    // Construct the full file path
    char full_path[PATH_MAX];
    snprintf(full_path, sizeof(full_path), "%s/%s", safe_path, filename);

    // Validate the full path to ensure it is within the allowed directory
    char resolved_path[PATH_MAX];
    if (realpath(full_path, resolved_path) == NULL || 
        strncmp(resolved_path, safe_path, strlen(safe_path)) != 0) {
        return strdup(""); // Return empty string if path traversal is detected
    }

    // Open the file for reading
    FILE *file = fopen(resolved_path, "r");
    if (file == NULL) {
        return strdup(""); // Return empty string if file cannot be opened
    }

    // Read the file content
    char *content = malloc(BUFFER_SIZE);
    if (content == NULL) {
        fclose(file);
        return strdup(""); // Return empty string if memory allocation fails
    }

    size_t total_read = 0;
    size_t bytes_read;
    while ((bytes_read = fread(content + total_read, 1, BUFFER_SIZE - total_read, file)) > 0) {
        total_read += bytes_read;
        if (total_read >= BUFFER_SIZE) {
            // Resize the content if necessary
            char *new_content = realloc(content, total_read + BUFFER_SIZE);
            if (new_content == NULL) {
                free(content);
                fclose(file);
                return strdup(""); // Return empty string if memory allocation fails
            }
            content = new_content;
        }
    }

    // Null-terminate the content
    content[total_read] = '\0';

    // Close the file and return the content
    fclose(file);
    return content;
}