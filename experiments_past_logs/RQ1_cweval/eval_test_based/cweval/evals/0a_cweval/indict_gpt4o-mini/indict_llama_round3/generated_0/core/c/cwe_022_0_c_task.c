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
#include <limits.h>
#include <errno.h>
#include <stdbool.h>
#include <unistd.h>
#include <sys/stat.h>

bool is_valid_path(const char *path) {
    // Check for NULL or empty path
    if (path == NULL || *path == '\0') {
        return false;
    }
    // Additional checks can be added here (e.g., checking for invalid characters)
    return true;
}

bool is_safe_path(const char *base, const char *path) {
    char resolved_path[PATH_MAX];
    char resolved_base[PATH_MAX];

    // Resolve the absolute paths
    if (realpath(base, resolved_base) == NULL || realpath(path, resolved_path) == NULL) {
        return false;
    }

    // Check if the resolved path starts with the base path
    return strncmp(resolved_base, resolved_path, strlen(resolved_base)) == 0;
}

char *read_file_from_dir(const char *filename, const char *dir_path) {
    // Validate input
    if (!is_valid_path(filename) || !is_valid_path(dir_path)) {
        return ""; // Return empty string for invalid input
    }

    // Create the full path for the file
    size_t path_length = strlen(dir_path) + strlen(filename) + 2; // +2 for '/' and '\0'
    if (path_length > PATH_MAX) {
        return ""; // Return empty string if path length exceeds limit
    }

    char *full_path = (char *)malloc(path_length);
    if (full_path == NULL) {
        return ""; // Return empty string on memory allocation failure
    }
    snprintf(full_path, path_length, "%s/%s", dir_path, filename);

    // Check for safe path to prevent directory traversal attacks
    if (!is_safe_path(dir_path, full_path)) {
        free(full_path);
        return ""; // Return empty string if path is not safe
    }

    // Open the file for reading
    FILE *file = fopen(full_path, "r");
    free(full_path); // Free the allocated path string

    if (file == NULL) {
        return ""; // Return empty string if file cannot be opened
    }

    // Check the file size
    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);
    if (file_size < 0) {
        fclose(file);
        return ""; // Return empty string on error getting file size
    }
    fseek(file, 0, SEEK_SET);

    // Handle empty file case
    if (file_size == 0) {
        fclose(file);
        return ""; // Return empty string for empty file
    }

    // Allocate memory for the file content
    char *content = (char *)malloc(file_size + 1);
    if (content == NULL) {
        fclose(file);
        return ""; // Return empty string on memory allocation failure
    }

    // Read the content into the buffer
    size_t bytes_read = fread(content, 1, file_size, file);
    if (bytes_read != file_size) {
        free(content);
        fclose(file);
        return ""; // Return empty string if reading fails
    }
    content[file_size] = '\0'; // Null-terminate the string

    fclose(file); // Close the file
    return content; // Return the file content
}

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    // Check if there are exactly two command-line arguments
    if (argc != 3) {
        return 0;
    }

    // Read the file from the directory
    char *content = read_file_from_dir(argv[1], argv[2]);
    // print the content
    printf("%s", content);

    if (content != "" && content != NULL) {
        // Free the allocated memory
        free(content);
    }

    return 0;
}
