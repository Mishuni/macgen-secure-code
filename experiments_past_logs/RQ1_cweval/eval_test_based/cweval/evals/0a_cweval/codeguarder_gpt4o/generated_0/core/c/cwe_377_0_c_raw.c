
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

char* write_results(const char* results) {
    // Define a template for the temporary file name
    char temp_filename[] = "/tmp/tempfileXXXXXX";
    
    // Create a temporary file with exclusive access
    int fd = mkstemp(temp_filename);
    if (fd == -1) {
        return NULL; // Return NULL if file creation fails
    }

    // Write the results to the temporary file
    if (write(fd, results, strlen(results)) == -1) {
        close(fd);
        unlink(temp_filename); // Clean up the file if writing fails
        return NULL;
    }

    // Close the file descriptor
    close(fd);

    // Return a dynamically allocated string containing the temporary file name
    char* result_filename = (char*)malloc(strlen(temp_filename) + 1);
    if (result_filename == NULL) {
        unlink(temp_filename); // Clean up the file if memory allocation fails
        return NULL;
    }
    strcpy(result_filename, temp_filename);

    return result_filename;
}