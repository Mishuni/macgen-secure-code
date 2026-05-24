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
