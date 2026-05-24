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
#include <dirent.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>
#include <limits.h>
#include <fcntl.h>

char *get_ls_result(const char *dir_path) {
    // Canonicalize the directory path to prevent directory traversal
    char real_path[PATH_MAX];
    if (realpath(dir_path, real_path) == NULL) {
        return NULL; // Return NULL if the path cannot be resolved
    }

    // Open the directory
    int dir_fd = open(real_path, O_RDONLY | O_DIRECTORY);
    if (dir_fd == -1) {
        return NULL; // Return NULL if the directory cannot be opened
    }

    DIR *dir = fdopendir(dir_fd);
    if (dir == NULL) {
        close(dir_fd);
        return NULL; // Return NULL if the directory cannot be opened
    }

    // Allocate initial memory for the result
    size_t buffer_size = 4096;
    char *result = malloc(buffer_size);
    if (result == NULL) {
        closedir(dir);
        return NULL; // Return NULL if memory allocation fails
    }
    result[0] = '\0'; // Initialize the result as an empty string

    struct dirent *entry;
    struct stat entry_info;
    size_t total_length = 0;

    // Read directory entries
    while ((entry = readdir(dir)) != NULL) {
        // Construct the full path for the entry
        char full_path[PATH_MAX];
        if (snprintf(full_path, sizeof(full_path), "%s/%s", real_path, entry->d_name) >= sizeof(full_path)) {
            continue; // Skip if the full path is too long
        }

        // Get file information using fstatat to avoid TOCTOU race conditions
        if (fstatat(dir_fd, entry->d_name, &entry_info, 0) == -1) {
            continue; // Skip if unable to get file information
        }

        // Format the entry information
        char entry_info_str[256];
        if (snprintf(entry_info_str, sizeof(entry_info_str), "%s\n", entry->d_name) >= sizeof(entry_info_str)) {
            continue; // Skip if the entry information is too long
        }

        // Check if the buffer needs to be resized
        size_t entry_length = strlen(entry_info_str);
        if (total_length + entry_length + 1 > buffer_size) {
            buffer_size *= 2;
            char *new_result = realloc(result, buffer_size);
            if (new_result == NULL) {
                free(result);
                closedir(dir);
                return NULL; // Return NULL if memory reallocation fails
            }
            result = new_result;
        }

        // Append the entry information to the result
        strncat(result, entry_info_str, entry_length);
        total_length += entry_length;
    }

    // Close the directory
    closedir(dir);

    return result;
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
