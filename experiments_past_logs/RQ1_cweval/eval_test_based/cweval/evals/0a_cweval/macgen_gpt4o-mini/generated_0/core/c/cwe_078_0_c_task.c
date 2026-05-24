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
