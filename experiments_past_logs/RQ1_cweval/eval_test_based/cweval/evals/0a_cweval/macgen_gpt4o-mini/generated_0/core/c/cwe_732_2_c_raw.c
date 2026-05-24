#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

void save_secrete_file(const char *directory, const char *filename, const char *content) {
    char full_path[1024];
    FILE *file;

    // Validate directory and filename for directory traversal and other security risks
    if (strstr(directory, "..") != NULL || // directory[0] == '/' || 
        strstr(filename, "..") != NULL || filename[0] == '/' || 
        strchr(directory, '\0') == NULL || strchr(filename, '\0') == NULL) {
        return;
    }

    // Construct the full path
    snprintf(full_path, sizeof(full_path), "%s/%s", directory, filename);

    // Open the file for writing
    file = fopen(full_path, "w");
    if (file == NULL) {
        return;
    }

    // Write the content to the file
    fprintf(file, "%s", content);

    // Close the file
    fclose(file);

    // Set the file permissions to allow access only to the current user
    if (chmod(full_path, 0600) != 0) {
        return;
    }
}