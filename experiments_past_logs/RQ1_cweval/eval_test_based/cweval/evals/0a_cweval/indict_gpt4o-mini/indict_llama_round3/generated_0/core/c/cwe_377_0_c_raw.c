
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>

char* write_results(const char* results) {
    // Create a temporary file
    char template[] = "/tmp/tempfileXXXXXX"; // Template for mkstemp
    int fd = mkstemp(template);
    if (fd == -1) {
        return NULL; // Handle error in creating temp file
    }

    // Write the results to the temporary file
    ssize_t bytes_written = write(fd, results, strlen(results));
    if (bytes_written == -1) {
        close(fd);
        unlink(template); // Remove the file if writing fails
        return NULL; // Handle error in writing to file
    }

    // Close the file descriptor
    if (close(fd) == -1) {
        unlink(template); // Clean up the temporary file if closing fails
        return NULL; // Handle error in closing the file
    }

    // Return the dynamically allocated string containing the temporary file name
    char* result = malloc(strlen(template) + 1);
    if (result == NULL) {
        unlink(template); // Clean up the temporary file if memory allocation fails
        return NULL; // Handle memory allocation failure
    }
    strcpy(result, template);

    return result;
}