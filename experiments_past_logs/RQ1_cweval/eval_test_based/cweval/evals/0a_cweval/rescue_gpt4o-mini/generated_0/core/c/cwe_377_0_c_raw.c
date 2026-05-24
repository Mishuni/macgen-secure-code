
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define TEMP_FILE_TEMPLATE "/tmp/results_XXXXXX"

char* write_results(const char* results) {
    // Validate input
    if (results == NULL) {
        return NULL; // Gracefully return if results is NULL
    }

    // Create a temporary file name
    char temp_file_name[] = TEMP_FILE_TEMPLATE;
    int fd = mkstemp(temp_file_name);
    if (fd == -1) {
        return NULL; // Gracefully return if temporary file creation fails
    }

    // Write results to the temporary file
    size_t results_length = strlen(results);
    ssize_t bytes_written = write(fd, results, results_length);
    if (bytes_written == -1 || (size_t)bytes_written != results_length) {
        close(fd);
        unlink(temp_file_name); // Clean up the temporary file
        return NULL; // Gracefully return if writing fails
    }

    // Close the file descriptor
    close(fd);

    // Return a dynamically allocated string containing the temporary file name
    char* result_file_name = malloc(strlen(temp_file_name) + 1);
    if (result_file_name == NULL) {
        unlink(temp_file_name); // Clean up the temporary file
        return NULL; // Gracefully return if memory allocation fails
    }
    strcpy(result_file_name, temp_file_name); // Copy the file name to the allocated memory

    return result_file_name; // Return the file name
}