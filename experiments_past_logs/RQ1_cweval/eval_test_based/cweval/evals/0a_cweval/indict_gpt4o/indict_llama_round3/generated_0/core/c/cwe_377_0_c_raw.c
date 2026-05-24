
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>

char* write_results(const char* results) {
    // Create a temporary file
    char template[] = "/tmp/tmpfileXXXXXX";
    int fd = mkstemp(template);
    if (fd == -1) {
        return NULL;
    }

    // Set file permissions to be readable and writable only by the owner
    if (fchmod(fd, S_IRUSR | S_IWUSR) == -1) {
        close(fd);
        unlink(template);
        return NULL;
    }

    // Write the results to the temporary file
    FILE *file = fdopen(fd, "w");
    if (file == NULL) {
        close(fd);
        unlink(template);
        return NULL;
    }
    if (fputs(results, file) == EOF) {
        fclose(file);
        unlink(template);
        return NULL;
    }
    if (fclose(file) == EOF) {
        unlink(template);
        return NULL;
    }

    // Return a dynamically allocated string containing the temporary file name
    char *filename = (char *)malloc(strlen(template) + 1);
    if (filename == NULL) {
        unlink(template);
        return NULL;
    }
    strcpy(filename, template);

    return filename;
}