#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>

#define MAX_LENGTH 1024

/**
 * Create a temporary file, write the provided results to it, and return the file name for further reading.
 *
 * @param results The string content to write to the temporary file
 * @return A dynamically allocated string containing the temporary file name. 
 *         Caller must free the returned string to avoid memory leaks.
 */
char* write_results(const char* results) {
    if (strlen(results) > MAX_LENGTH) {
        return NULL;
    }

    char template[] = "/tmp/tempfileXXXXXX";
    int fd = mkstemp(template);
    if (fd == -1) {
        return NULL;
    }

    FILE* temp_file = fdopen(fd, "w");
    if (temp_file == NULL) {
        close(fd);
        return NULL;
    }

    if (fprintf(temp_file, "%s", results) < 0) {
        fclose(temp_file);
        return NULL;
    }

    fclose(temp_file);

    // Return the modified template which contains the correct filename
    return strdup(template); // Caller must free this string
}