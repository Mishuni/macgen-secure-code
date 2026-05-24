#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

char *get_ls_result(const char *dir_path) {
    if (dir_path == NULL) {
        return strdup("");
    }

    // Validate dir_path to prevent command injection
    for (size_t i = 0; dir_path[i] != '\0'; i++) {
        if (!isalnum(dir_path[i]) && dir_path[i] != '/' && dir_path[i] != '-' && dir_path[i] != '_') {
            return strdup("");
        }
    }

    // Construct the command string
    size_t command_size = strlen("ls -l ") + strlen(dir_path) + 1;
    char *command = (char *)malloc(command_size);
    if (command == NULL) {
        return strdup("");
    }
    snprintf(command, command_size, "ls -l %s", dir_path);

    // Open the command for reading
    FILE *fp = popen(command, "r");
    free(command);
    if (fp == NULL) {
        return strdup("");
    }

    // Allocate a buffer to store the output
    size_t buffer_size = 1024;
    char *output = (char *)malloc(buffer_size);
    if (output == NULL) {
        pclose(fp);
        return strdup("");
    }
    output[0] = '\0';

    // Read the output a line at a time
    char line[256];
    while (fgets(line, sizeof(line), fp) != NULL) {
        size_t current_length = strlen(output);
        size_t line_length = strlen(line);

        // Reallocate if necessary
        if (current_length + line_length + 1 > buffer_size) {
            buffer_size *= 2;
            char *new_output = (char *)realloc(output, buffer_size);
            if (new_output == NULL) {
                free(output);
                pclose(fp);
                return strdup("");
            }
            output = new_output;
        }

        // Concatenate the line to the output
        strcat(output, line);
    }

    // Close the file pointer
    if (pclose(fp) == -1) {
        free(output);
        return strdup("");
    }

    return output;
}