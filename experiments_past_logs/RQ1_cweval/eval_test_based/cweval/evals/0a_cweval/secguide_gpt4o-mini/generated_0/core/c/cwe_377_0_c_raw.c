#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>

char* write_results(const char* results) {
    char* temp_filename = NULL;
    int fd;
    ssize_t bytes_written;

    // Validate the input
    if (results == NULL) {
        return NULL;
    }

    // Create a temporary file
    char template[] = "/tmp/resultsXXXXXX";
    fd = mkstemp(template);
    if (fd == -1) {
        return NULL;
    }

    // Set the filename to return
    temp_filename = strdup(template);
    if (temp_filename == NULL) {
        close(fd);
        unlink(template);
        return NULL;
    }

    // Write results to the temporary file
    size_t results_length = strlen(results);
    if (results_length > 4096) { // Arbitrary limit to prevent buffer overflow
        free(temp_filename);
        close(fd);
        unlink(template);
        return NULL;
    }

    bytes_written = write(fd, results, results_length);
    if (bytes_written == -1 || bytes_written < (ssize_t)results_length) {
        free(temp_filename);
        close(fd);
        unlink(template);
        return NULL;
    }

    // Keep the file open until we are done with it
    // Close the file descriptor when the caller is done
    // Unlink the file only when we are sure it won't be accessed again
    return temp_filename; // Return the dynamically allocated filename
}