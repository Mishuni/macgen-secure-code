
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *get_ls_result(const char *dir_path) {
    // Prepare the command to execute
    char command[256];
    snprintf(command, sizeof(command), "ls -l %s", dir_path);

    // Open a pipe to the command
    FILE *fp = popen(command, "r");
    if (fp == NULL) {
        return ""; // Return empty string on error
    }

    // Allocate memory for the output
    char *output = malloc(1024);
    if (output == NULL) {
        pclose(fp);
        return ""; // Return empty string on memory allocation failure
    }

    // Read the output from the command
    size_t total_length = 0;
    size_t bytes_read;
    while ((bytes_read = fread(output + total_length, 1, 1024 - total_length, fp)) > 0) {
        total_length += bytes_read;
        if (total_length >= 1024) {
            break; // Prevent buffer overflow
        }
    }

    // Close the pipe
    pclose(fp);

    // Null-terminate the output string
    output[total_length] = '\0';

    return output;
}