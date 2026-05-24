
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <errno.h>

char *get_ls_result(const char *dir_path) {
    struct stat stat_buf;
    char *output = NULL;
    FILE *fp;
    char command[256];

    // Validate the directory path
    if (dir_path == NULL || strlen(dir_path) == 0) {
        return "";
    }

    // Check if the directory exists and is accessible
    if (stat(dir_path, &stat_buf) != 0 || !S_ISDIR(stat_buf.st_mode)) {
        return "";
    }

    // Construct the command safely
    snprintf(command, sizeof(command), "ls -l %s", dir_path);

    // Execute the command
    fp = popen(command, "r");
    if (fp == NULL) {
        return "";
    }

    // Allocate memory for the output
    size_t size = 1024;
    output = malloc(size);
    if (output == NULL) {
        pclose(fp);
        return "";
    }

    // Read the output
    size_t total_read = 0;
    while (fgets(output + total_read, size - total_read, fp) != NULL) {
        total_read += strlen(output + total_read);
        if (total_read >= size - 1) {
            size *= 2;
            char *new_output = realloc(output, size);
            if (new_output == NULL) {
                free(output);
                pclose(fp);
                return "";
            }
            output = new_output;
        }
    }

    // Close the command stream
    if (pclose(fp) == -1) {
        free(output);
        return "";
    }

    return output;
}