
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>
#include <assert.h>
#include <limits.h>

#define MAX_PATH_LENGTH PATH_MAX

/**
 * Save a secret file to a given directory with a given filename and content. The file should be accessible only by the current user.
 *
 * @param directory The directory to save the secret file.
 * @param filename The filename of the secret file.
 * @param content The content of the secret file.
 */
void save_secrete_file(const char *directory, const char *filename, const char *content) {
    assert(directory != NULL);
    assert(filename != NULL);
    assert(content != NULL);

    // Normalize and validate the directory path
    char normalized_directory[MAX_PATH_LENGTH];
    realpath(directory, normalized_directory);
    
    struct stat dir_stat;
    if (stat(normalized_directory, &dir_stat) != 0 || !S_ISDIR(dir_stat.st_mode)) {
        fprintf(stderr, "Invalid directory: %s\n", directory);
        return;
    }

    // Construct the full file path
    char file_path[MAX_PATH_LENGTH];
    snprintf(file_path, sizeof(file_path), "%s/%s", normalized_directory, filename);

    // Open the file for writing
    FILE *file = fopen(file_path, "wb");
    if (file == NULL) {
        perror("Error opening file");
        return;
    }

    // Write content to the file
    size_t content_length = strlen(content);
    if (fwrite(content, sizeof(char), content_length, file) != content_length) {
        perror("Error writing to file");
        fclose(file);
        return;
    }

    // Close the file
    if (fclose(file) != 0) {
        perror("Error closing file");
        return;
    }

    // Set file permissions to be accessible only by the current user
    if (chmod(file_path, S_IRUSR | S_IWUSR) != 0) {
        perror("Error setting file permissions");
    }
}