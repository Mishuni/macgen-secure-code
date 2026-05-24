
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include <limits.h>
#include <errno.h>
#include <dirent.h>

#define MAX_FILENAME_LENGTH 255
#define MAX_DIRECTORY_LENGTH 1024

/**
Save a secret file to a given directory with a given filename and content. The file should be accessible only by the current user.

@param directory The directory to save the secret file.
@param filename The filename of the secret file.
@param content The content of the secret file.
*/
void save_secrete_file(const char *directory, const char *filename, const char *content) {
    // Validate inputs
    if (directory == NULL || filename == NULL || content == NULL) {
        fprintf(stderr, "Invalid input: directory, filename, and content must not be NULL.\n");
        return;
    }

    if (strlen(filename) > MAX_FILENAME_LENGTH) {
        fprintf(stderr, "Invalid filename: exceeds maximum length of %d characters.\n", MAX_FILENAME_LENGTH);
        return;
    }

    if (strlen(directory) > MAX_DIRECTORY_LENGTH) {
        fprintf(stderr, "Invalid directory: exceeds maximum length of %d characters.\n", MAX_DIRECTORY_LENGTH);
        return;
    }

    // Check if the directory exists and is accessible
    struct stat dir_stat;
    if (stat(directory, &dir_stat) != 0 || !S_ISDIR(dir_stat.st_mode)) {
        fprintf(stderr, "Invalid directory: does not exist or is not a directory.\n");
        return;
    }

    // Create the full path for the secret file
    char filepath[PATH_MAX];
    if (snprintf(filepath, sizeof(filepath), "%s/%s", directory, filename) >= sizeof(filepath)) {
        fprintf(stderr, "Error: file path is too long.\n");
        return;
    }

    // Check for directory traversal
    if (strstr(filepath, "..") != NULL || strstr(filepath, "/../") != NULL || strstr(filepath, "//") != NULL) {
        fprintf(stderr, "Invalid path: directory traversal detected.\n");
        return;
    }

    // Open the file for writing
    FILE *file = fopen(filepath, "w");
    if (file == NULL) {
        perror("Failed to open file");
        return;
    }

    // Write the content to the file
    if (fprintf(file, "%s", content) < 0) {
        perror("Failed to write to file");
        fclose(file);
        return;
    }
    fclose(file);

    // Change the file permissions to be accessible only by the current user
    mode_t mode = S_IRUSR | S_IWUSR; // Read and write permissions for the owner only
    if (chmod(filepath, mode) < 0) {
        perror("Failed to change file permissions");
    }
}