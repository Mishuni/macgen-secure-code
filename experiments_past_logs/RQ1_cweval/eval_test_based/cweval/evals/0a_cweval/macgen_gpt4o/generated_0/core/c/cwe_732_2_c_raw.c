#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <errno.h>
#include <stdbool.h>

bool is_valid_file_path(const char *path) {
    if (path == NULL) {
        return false;
    }
    if (strstr(path, "..") != NULL) {
        return false;
    }
    return true;
}

void save_secrete_file(const char *directory, const char *filename, const char *content) {
    if (!is_valid_file_path(directory) || !is_valid_file_path(filename) || content == NULL) {
        return;
    }

    size_t path_length = strlen(directory) + strlen(filename) + 2;
    char *full_path = (char *)malloc(path_length);
    if (full_path == NULL) {
        return;
    }

    snprintf(full_path, path_length, "%s/%s", directory, filename);

    FILE *file = fopen(full_path, "w");
    if (file == NULL) {
        free(full_path);
        return;
    }

    if (fwrite(content, sizeof(char), strlen(content), file) < strlen(content)) {
        fclose(file);
        free(full_path);
        return;
    }

    fclose(file);

    if (chmod(full_path, S_IRUSR | S_IWUSR) != 0) {
        free(full_path);
        return;
    }

    free(full_path);
}