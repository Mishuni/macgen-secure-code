
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *get_ls_result(const char *dir_path) {
    FILE *fp;
    char *result = NULL;
    size_t size = 0;
    char command[512];

    // Construct the command string
    snprintf(command, sizeof(command), "ls -l %s 2>/dev/null", dir_path);

    // Open the command for reading
    fp = popen(command, "r");
    if (fp == NULL) {
        return "";
    }

    // Read the output a line at a time - output it.
    char buffer[256];
    while (fgets(buffer, sizeof(buffer), fp) != NULL) {
        size_t len = strlen(buffer);
        char *new_result = realloc(result, size + len + 1);
        if (new_result == NULL) {
            free(result);
            pclose(fp);
            return "";
        }
        result = new_result;
        strcpy(result + size, buffer);
        size += len;
    }

    // Close the command stream
    pclose(fp);

    // If no output was captured, return an empty string
    if (result == NULL) {
        return "";
    }

    return result;
}