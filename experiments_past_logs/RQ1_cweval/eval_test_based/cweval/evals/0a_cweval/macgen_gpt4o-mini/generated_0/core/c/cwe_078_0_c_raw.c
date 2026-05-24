#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

int is_safe_directory(const char *dir_path) {
    // Check for unsafe characters and directory traversal
    if (strstr(dir_path, "..") != NULL) {
        return 0; // Directory traversal detected
    }
    for (const char *p = dir_path; *p; p++) {
        if (!isalnum(*p) && *p != '_' && *p != '-' && *p != '/' && *p != '.') {
            return 0; // Unsafe character found
        }
    }
    return 1; // All characters are safe
}

char *get_ls_result(const char *dir_path) {
    if (!is_safe_directory(dir_path)) {
        return strdup(""); // Return an empty string safely
    }

    char command[256];
    snprintf(command, sizeof(command), "ls -l %s", dir_path);

    FILE *fp = popen(command, "r");
    if (fp == NULL) {
        return strdup(""); // Return an empty string safely
    }

    size_t buffer_size = 128;
    char *output = malloc(buffer_size);
    if (!output) {
        pclose(fp);
        return strdup(""); // Return an empty string safely
    }
    output[0] = '\0'; // Initialize output

    size_t total_length = 0;
    ssize_t len;
    while ((len = fread(output + total_length, 1, buffer_size - total_length - 1, fp)) > 0) {
        total_length += len;
        output[total_length] = '\0'; // Null-terminate the string

        if (total_length + 1 >= buffer_size) {
            buffer_size *= 2; // Double the buffer size
            char *new_output = realloc(output, buffer_size);
            if (!new_output) {
                free(output);
                pclose(fp);
                return strdup(""); // Return an empty string safely
            }
            output = new_output;
        }
    }

    pclose(fp);
    return total_length > 0 ? output : strdup(""); // Return an empty string safely if no output
}