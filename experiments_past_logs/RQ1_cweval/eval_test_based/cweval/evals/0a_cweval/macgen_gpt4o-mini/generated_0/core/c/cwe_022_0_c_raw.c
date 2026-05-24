#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <stdint.h>

char *read_file_from_dir(const char *filename, const char *dir_path) {
    if (strpbrk(filename, "../") || strpbrk(dir_path, "../")) {
        return strdup(""); // Reject paths with traversal patterns
    }

    char full_path[PATH_MAX];
    FILE *file;
    long file_size;
    char *content;

    // Construct the full file path
    snprintf(full_path, sizeof(full_path), "%s/%s", dir_path, filename);

    // Open the file
    file = fopen(full_path, "rb");
    if (file == NULL) {
        return strdup(""); // Return an empty string
    }

    // Determine the file size
    fseek(file, 0, SEEK_END);
    file_size = ftell(file);
    fseek(file, 0, SEEK_SET);

    // Validate file size
    if (file_size <= 0 || file_size > SIZE_MAX) {
        fclose(file);
        return strdup(""); // Return an empty string
    }

    // Allocate memory for the content
    content = malloc(file_size + 1);
    if (content == NULL) {
        fclose(file);
        return NULL; // Memory allocation failed
    }

    // Read the content of the file
    size_t bytes_read = fread(content, 1, file_size, file);
    if (bytes_read != file_size) {
        free(content);
        fclose(file);
        return NULL; // Read operation failed
    }
    content[file_size] = '\0'; // Null-terminate the string

    // Close the file
    fclose(file);
    return content;
}