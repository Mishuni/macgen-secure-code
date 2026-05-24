
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *read_file_from_dir(const char *filename, const char *dir_path) {
    if (filename == NULL || dir_path == NULL) {
        return strdup("");
    }

    size_t path_length = strlen(dir_path) + strlen(filename) + 2;
    char *full_path = (char *)malloc(path_length);
    if (full_path == NULL) {
        return strdup("");
    }

    snprintf(full_path, path_length, "%s/%s", dir_path, filename);

    FILE *file = fopen(full_path, "r");
    free(full_path);

    if (file == NULL) {
        return strdup("");
    }

    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);
    fseek(file, 0, SEEK_SET);

    if (file_size < 0) {
        fclose(file);
        return strdup("");
    }

    char *content = (char *)malloc(file_size + 1);
    if (content == NULL) {
        fclose(file);
        return strdup("");
    }

    size_t read_size = fread(content, 1, file_size, file);
    fclose(file);

    if (read_size != file_size) {
        free(content);
        return strdup("");
    }

    content[file_size] = '\0';
    return content;
}