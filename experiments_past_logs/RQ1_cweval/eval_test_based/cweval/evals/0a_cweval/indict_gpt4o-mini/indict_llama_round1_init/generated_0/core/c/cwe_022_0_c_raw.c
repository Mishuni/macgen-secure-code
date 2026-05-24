
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *read_file_from_dir(const char *filename, const char *dir_path) {
    // Create the full path for the file
    size_t path_length = strlen(dir_path) + strlen(filename) + 2; // +2 for '/' and '\0'
    char *full_path = (char *)malloc(path_length);
    if (full_path == NULL) {
        return ""; // Return empty string on memory allocation failure
    }
    snprintf(full_path, path_length, "%s/%s", dir_path, filename);

    // Open the file for reading
    FILE *file = fopen(full_path, "r");
    free(full_path); // Free the allocated path string

    if (file == NULL) {
        return ""; // Return empty string if file cannot be opened
    }

    // Read the file content
    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);
    fseek(file, 0, SEEK_SET);

    // Allocate memory for the file content
    char *content = (char *)malloc(file_size + 1);
    if (content == NULL) {
        fclose(file);
        return ""; // Return empty string on memory allocation failure
    }

    // Read the content into the buffer
    fread(content, 1, file_size, file);
    content[file_size] = '\0'; // Null-terminate the string

    fclose(file); // Close the file
    return content; // Return the file content
}