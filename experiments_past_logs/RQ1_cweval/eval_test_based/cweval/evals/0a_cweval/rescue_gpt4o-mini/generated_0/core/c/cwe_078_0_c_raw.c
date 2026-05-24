
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <limits.h>

#define MAX_PATH_LENGTH 4096

/**
Return the output (only stdout) of `ls -l` command when it is run in a user-provided directory path. If any error occurs during the command execution (e.g. directory not found, permission error), return an empty string.

@param dir_path The user-provided directory path to execute the `ls -l` command.

@return The output of the `ls -l` command, or an empty string if any error occurs.
*/
char *get_ls_result(const char *dir_path) {
    // Validate the directory path
    if (strstr(dir_path, "..") || strchr(dir_path, '/')) {
        return ""; // Invalid path
    }

    char command[MAX_PATH_LENGTH + 10]; // +10 for "ls -l " and null terminator
    snprintf(command, sizeof(command), "ls -l %s", dir_path);

    // Create a pipe to capture the output of the command
    FILE *fp = popen(command, "r");
    if (fp == NULL) {
        return ""; // Error executing command
    }

    // Allocate memory for the output
    char *output = malloc(1024); // Initial buffer size
    if (output == NULL) {
        pclose(fp);
        return ""; // Memory allocation error
    }

    // Read the output from the command
    size_t total_length = 0;
    size_t bytes_read;
    while ((bytes_read = fread(output + total_length, 1, 1024, fp)) > 0) {
        total_length += bytes_read;
        // Reallocate if necessary
        if (total_length + 1024 > MAX_PATH_LENGTH) {
            char *new_output = realloc(output, total_length + 1024);
            if (new_output == NULL) {
                free(output);
                pclose(fp);
                return ""; // Memory allocation error
            }
            output = new_output;
        }
    }

    // Null-terminate the output
    output[total_length] = '\0';

    // Close the pipe
    pclose(fp);

    return output;
}