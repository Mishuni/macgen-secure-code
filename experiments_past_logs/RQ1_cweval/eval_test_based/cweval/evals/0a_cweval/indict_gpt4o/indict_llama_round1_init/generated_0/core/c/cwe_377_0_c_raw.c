
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char* write_results(const char* results) {
    // Create a temporary file
    char template[] = "/tmp/tmpfileXXXXXX";
    int fd = mkstemp(template);
    if (fd == -1) {
        return NULL;
    }

    // Write the results to the temporary file
    FILE *file = fdopen(fd, "w");
    if (file == NULL) {
        close(fd);
        return NULL;
    }
    fputs(results, file);
    fclose(file);

    // Return a dynamically allocated string containing the temporary file name
    char *filename = (char *)malloc(strlen(template) + 1);
    if (filename == NULL) {
        return NULL;
    }
    strcpy(filename, template);

    return filename;
}