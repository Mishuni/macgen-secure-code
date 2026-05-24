#include <archive_entry.h>
#include <jwt.h>
#include <errno.h>
#include <sys/wait.h>
#include <libxml/xpath.h>
#include <sqlite3.h>
#include <archive.h>
#include <ctype.h>
#include <libxml/parser.h>
#include <openssl/evp.h>
#include <openssl/des.h>
#include <openssl/aes.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <openssl/md5.h>
#include <stdlib.h>
#include <libgen.h>
#include <sys/types.h>
#include <stdio.h>
#include <stdbool.h>
#include <time.h>
#include <string.h>
#include <openssl/sha.h>
#include <regex.h>
#include <unistd.h>
#include <openssl/rand.h>
#include <archive.h>
#include <archive_entry.h>
#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <jwt.h>
#include <libgen.h>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <openssl/aes.h>
#include <openssl/des.h>
#include <openssl/evp.h>
#include <openssl/md5.h>
#include <openssl/rand.h>
#include <openssl/sha.h>
#include <regex.h>
#include <sqlite3.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

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

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    // Check if there is exactly one command-line argument
    if (argc != 2) {
        return 0;
    }

    // Get the output of the `ls -l` command
    char *output = get_ls_result(argv[1]);
    // Print the output
    printf("%s", output);
    
    if (output != "" && output != NULL) {
        // Free the allocated memory
        free(output);
    }

    return 0;
}
