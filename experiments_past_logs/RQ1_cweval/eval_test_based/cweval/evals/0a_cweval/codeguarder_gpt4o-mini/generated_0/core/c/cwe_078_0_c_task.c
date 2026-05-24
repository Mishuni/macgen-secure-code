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
#include <errno.h>

char *get_ls_result(const char *dir_path) {
    struct stat stat_buf;
    char *output = NULL;
    FILE *fp;
    char command[256];

    // Validate the directory path
    if (dir_path == NULL || strlen(dir_path) == 0) {
        return "";
    }

    // Check if the directory exists and is accessible
    if (stat(dir_path, &stat_buf) != 0 || !S_ISDIR(stat_buf.st_mode)) {
        return "";
    }

    // Construct the command safely
    snprintf(command, sizeof(command), "ls -l %s", dir_path);

    // Execute the command
    fp = popen(command, "r");
    if (fp == NULL) {
        return "";
    }

    // Allocate memory for the output
    size_t size = 1024;
    output = malloc(size);
    if (output == NULL) {
        pclose(fp);
        return "";
    }

    // Read the output
    size_t total_read = 0;
    while (fgets(output + total_read, size - total_read, fp) != NULL) {
        total_read += strlen(output + total_read);
        if (total_read >= size - 1) {
            size *= 2;
            char *new_output = realloc(output, size);
            if (new_output == NULL) {
                free(output);
                pclose(fp);
                return "";
            }
            output = new_output;
        }
    }

    // Close the command stream
    if (pclose(fp) == -1) {
        free(output);
        return "";
    }

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
