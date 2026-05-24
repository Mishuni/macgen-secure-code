
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>

bool is_valid_directory(const char *dir_path) {
    struct stat statbuf;
    return (stat(dir_path, &statbuf) == 0 && S_ISDIR(statbuf.st_mode));
}

char *get_ls_result(const char *dir_path) {
    // Validate the directory path
    if (!is_valid_directory(dir_path)) {
        return ""; // Return empty string if path is invalid or not a directory
    }

    // Prepare the command to execute
    char command[256];
    snprintf(command, sizeof(command), "ls -l \"%s\"", dir_path);

    // Open a pipe to the command
    FILE *fp = popen(command, "r");
    if (fp == NULL) {
        return ""; // Return empty string on error
    }

    // Allocate memory for the output
    size_t output_size = 1024;
    char *output = malloc(output_size);
    if (output == NULL) {
        pclose(fp);
        return ""; // Return empty string on memory allocation failure
    }

    // Read the output from the command
    size_t total_length = 0;
    size_t bytes_read;
    while ((bytes_read = fread(output + total_length, 1, output_size - total_length, fp)) > 0) {
        total_length += bytes_read;
        if (total_length >= output_size) {
            output_size *= 2; // Double the buffer size
            char *new_output = realloc(output, output_size);
            if (new_output == NULL) {
                free(output);
                pclose(fp);
                return ""; // Return empty string on memory allocation failure
            }
            output = new_output;
        }
    }

    // Close the pipe
    pclose(fp);

    // Null-terminate the output string
    output[total_length] = '\0';

    return output;
}