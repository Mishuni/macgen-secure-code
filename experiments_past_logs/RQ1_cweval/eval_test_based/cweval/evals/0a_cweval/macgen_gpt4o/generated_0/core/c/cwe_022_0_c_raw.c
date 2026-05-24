#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <sys/stat.h>
#include <unistd.h>

char *read_file_from_dir(const char *filename, const char *dir_path) {
    if (!filename || !dir_path) {
        return strdup("");
    }

    // Check for path traversal in filename
    if (strstr(filename, "..") != NULL) {
        return strdup("");
    }

    char resolved_dir_path[PATH_MAX];
    if (!realpath(dir_path, resolved_dir_path)) {
        return strdup("");
    }

    size_t path_len = strlen(resolved_dir_path) + strlen(filename) + 2;
    char *full_path = (char *)malloc(path_len);
    if (!full_path) {
        return strdup("");
    }

    snprintf(full_path, path_len, "%s/%s", resolved_dir_path, filename);

    FILE *file = fopen(full_path, "rb");
    free(full_path);

    if (!file) {
        return strdup("");
    }

    struct stat file_stat;
    if (fstat(fileno(file), &file_stat) != 0 || !S_ISREG(file_stat.st_mode)) {
        fclose(file);
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
    if (!content) {
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