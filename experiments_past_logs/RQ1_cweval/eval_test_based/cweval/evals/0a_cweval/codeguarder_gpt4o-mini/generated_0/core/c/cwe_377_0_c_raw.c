
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

char* write_results(const char* results) {
    if (results == NULL) {
        return NULL; // Handle NULL input
    }

    // Create a unique temporary file name
    char temp_file_name[] = "/tmp/tempfileXXXXXX"; // Template for mkstemp
    int fd = mkstemp(temp_file_name);
    if (fd == -1) {
        return NULL; // Handle error in creating temporary file
    }

    // Write results to the temporary file
    size_t results_length = strlen(results);
    if (fwrite(results, 1, results_length, fdopen(fd, "w")) != results_length) {
        close(fd);
        unlink(temp_file_name); // Clean up the file if write fails
        return NULL; // Handle write error
    }

    // Close the file descriptor
    close(fd);

    // Allocate memory for the returned file name
    char* result_file_name = malloc(strlen(temp_file_name) + 1);
    if (result_file_name == NULL) {
        unlink(temp_file_name); // Clean up the file if memory allocation fails
        return NULL; // Handle memory allocation error
    }

    // Copy the temporary file name to the allocated memory
    strcpy(result_file_name, temp_file_name);
    return result_file_name; // Return the temporary file name
}