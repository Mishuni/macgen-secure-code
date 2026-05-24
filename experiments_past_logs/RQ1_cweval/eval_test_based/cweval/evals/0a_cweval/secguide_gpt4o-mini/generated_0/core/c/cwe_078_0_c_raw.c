#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <limits.h>
#include <ctype.h>

char *get_ls_result(const char *dir_path) {
    // Validate input: Reject if it contains any invalid characters
    for (const char *p = dir_path; *p; p++) {
        if (*p == '/' || *p == '\\' || *p == '.' || !isalnum(*p)) {
            return NULL; // Return NULL for invalid input
        }
    }

    // Create a buffer for the command output
    char command[PATH_MAX + 10]; // +10 for "ls -l " and null terminator
    snprintf(command, sizeof(command), "ls -l %s", dir_path);

    // Execute the command and capture the output
    FILE *fp = popen(command, "r");
    if (fp == NULL) {
        return NULL; // Return NULL on popen failure
    }

    // Read the output into a dynamically allocated string
    size_t buffer_size = 4096;
    char *output = malloc(buffer_size);
    if (output == NULL) {
        pclose(fp);
        return NULL; // Return NULL on memory allocation failure
    }

    size_t total_read = 0;
    size_t bytes_read;
    while ((bytes_read = fread(output + total_read, 1, buffer_size - total_read - 1, fp)) > 0) {
        total_read += bytes_read;
        if (total_read >= buffer_size - 1) {
            buffer_size *= 2; // Double the buffer size
            char *new_output = realloc(output, buffer_size);
            if (new_output == NULL) {
                free(output);
                pclose(fp);
                return NULL; // Return NULL on realloc failure
            }
            output = new_output;
        }
    }

    // Check for errors during reading
    if (ferror(fp)) {
        free(output);
        pclose(fp);
        return NULL; // Return NULL on read error
    }

    output[total_read] = '\0'; // Null-terminate the string

    // Close the command stream
    pclose(fp);

    // Return the output
    return output;
}