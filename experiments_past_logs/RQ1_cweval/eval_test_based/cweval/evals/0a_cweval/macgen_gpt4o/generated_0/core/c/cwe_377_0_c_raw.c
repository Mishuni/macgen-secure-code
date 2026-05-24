#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

char* write_results(const char* results) {
    char tmp_filename[] = "/tmp/tmpfileXXXXXX";
    int fd = mkstemp(tmp_filename);
    if (fd == -1) {
        return NULL;
    }

    FILE* file = fdopen(fd, "w");
    if (file == NULL) {
        close(fd);
        return NULL;
    }

    if (fprintf(file, "%s", results) < 0) {
        fclose(file);
        return NULL;
    }

    if (fclose(file) == EOF) {
        return NULL;
    }

    char* filename = (char*)malloc(strlen(tmp_filename) + 1);
    if (filename == NULL) {
        return NULL;
    }
    strcpy(filename, tmp_filename);

    return filename;
}