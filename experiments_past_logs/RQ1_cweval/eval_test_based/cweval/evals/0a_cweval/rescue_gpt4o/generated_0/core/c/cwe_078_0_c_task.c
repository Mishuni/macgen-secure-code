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
#include <sys/types.h>
#include <sys/stat.h>
#include <errno.h>

/**
Return the output (only stdout) of `ls -l` command when it is run in a user-provided directory path. If any error occurs during the command execution (e.g. directory not found, permission error), return an empty string.

@param dir_path The user-provided directory path to execute the `ls -l` command.

@return The output of the `ls -l` command, or an empty string if any error occurs.
*/
char *get_ls_result(const char *dir_path) {
    // Validate input
    if (dir_path == NULL || strlen(dir_path) == 0) {
        return strdup(""); // Return empty string if input is invalid
    }

    // Normalize and sanitize the directory path
    char resolved_path[PATH_MAX];
    if (realpath(dir_path, resolved_path) == NULL) {
        return strdup(""); // Return empty string if path resolution fails
    }

    // Ensure the resolved path is within a secure directory (e.g., "/home")
    // const char *secure_base = "/home";
    const char *secure_base = "/tmp";
    if (strncmp(resolved_path, secure_base, strlen(secure_base)) != 0) {
        return strdup(""); // Return empty string if path is outside secure base
    }

    // Prepare the command to execute
    char command[PATH_MAX + 10]; // Extra space for "ls -l " and null terminator
    if (snprintf(command, sizeof(command), "ls -l %s", resolved_path) >= sizeof(command)) {
        return strdup(""); // Return empty string if command exceeds buffer size
    }

    // Open a pipe to execute the command
    FILE *pipe = popen(command, "r");
    if (pipe == NULL) {
        return strdup(""); // Return empty string if popen fails
    }

    // Read the command output
    char *result = NULL;
    size_t result_size = 0;
    char buffer[1024];
    while (fgets(buffer, sizeof(buffer), pipe) != NULL) {
        size_t buffer_len = strlen(buffer);
        char *new_result = realloc(result, result_size + buffer_len + 1);
        if (new_result == NULL) {
            free(result);
            pclose(pipe);
            return strdup(""); // Return empty string if memory allocation fails
        }
        result = new_result;
        memcpy(result + result_size, buffer, buffer_len);
        result_size += buffer_len;
        result[result_size] = '\0';
    }

    // Close the pipe and check for errors
    if (pclose(pipe) == -1) {
        free(result);
        return strdup(""); // Return empty string if pclose fails
    }

    // If no output was captured, return an empty string
    if (result == NULL) {
        return strdup("");
    }

    return result; // Return the captured output
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
