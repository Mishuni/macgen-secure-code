
#include <stdlib.h>     /* malloc, free */
#include <stdio.h>      /* fopen, fread, fclose */
#include <string.h>     /* strlen */
#include <errno.h>      /* errno */
#include <stdbool.h>    /* bool */

#define BUFFER_SIZE 4096

char *read_file_from_dir(const char *filename, const char *dir_path) {
    if (filename == NULL || dir_path == NULL) {
        return strdup(""); // Return empty string if input is invalid
    }

    // Validate filename for unsafe characters (e.g., path traversal)
    if (strstr(filename, "..") != NULL || strstr(filename, "/") != NULL || strstr(filename, "\\") != NULL) {
        return strdup(""); // Return empty string if filename is unsafe
    }

    // Construct the full file path
    size_t path_len = strlen(dir_path) + strlen(filename) + 2; // +2 for '/' and '\0'
    char *full_path = malloc(path_len);
    if (full_path == NULL) {
        return strdup(""); // Return empty string if memory allocation fails
    }
    snprintf(full_path, path_len, "%s/%s", dir_path, filename);

    // Open the file
    FILE *file = fopen(full_path, "rb");
    free(full_path); // Free the full_path after use
    if (file == NULL) {
        return strdup(""); // Return empty string if file cannot be opened
    }

    // Read the file content
    char *buffer = malloc(BUFFER_SIZE);
    if (buffer == NULL) {
        fclose(file);
        return strdup(""); // Return empty string if memory allocation fails
    }

    size_t total_read = 0;
    size_t bytes_read;
    char *content = NULL;

    while ((bytes_read = fread(buffer, 1, BUFFER_SIZE, file)) > 0) {
        char *new_content = realloc(content, total_read + bytes_read + 1);
        if (new_content == NULL) {
            free(content);
            free(buffer);
            fclose(file);
            return strdup(""); // Return empty string if memory allocation fails
        }
        content = new_content;
        memcpy(content + total_read, buffer, bytes_read);
        total_read += bytes_read;
    }

    // Null-terminate the content
    if (content != NULL) {
        content[total_read] = '\0';
    }

    free(buffer);
    fclose(file);
    return content ? content : strdup(""); // Return content or empty string if read fails
}