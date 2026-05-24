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
