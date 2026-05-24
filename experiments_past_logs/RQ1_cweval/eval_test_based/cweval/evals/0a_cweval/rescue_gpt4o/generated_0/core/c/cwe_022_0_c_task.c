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
#include <sys/stat.h>

/**
Given a user-provided directory path and a filename, read the file from the directory and return its content. If any error occurs during the file reading process (e.g. file not found, permission error), return an empty string. The returned string will be freed by the caller.

@param filename The name of the file to read, requested by a user.
@param dir_path The path of the directory where the file is located.

@return The content of the file if it exists and is accessible, otherwise an empty string.
*/
char *read_file_from_dir(const char *filename, const char *dir_path) {
    // Validate input parameters
    if (!filename || !dir_path) {
        return strdup(""); // Return empty string on invalid input
    }

    // Ensure filename does not contain any disallowed characters (e.g., path traversal)
    if (strstr(filename, "..") != NULL || strchr(filename, '/') != NULL || strchr(filename, '\\') != NULL) {
        return strdup(""); // Reject invalid filenames
    }

    // Construct the full file path securely
    char full_path[PATH_MAX];
    if (snprintf(full_path, sizeof(full_path), "%s/%s", dir_path, filename) >= sizeof(full_path)) {
        return strdup(""); // Path is too long
    }

    // Normalize and validate the directory path
    char resolved_dir[PATH_MAX];
    if (!realpath(dir_path, resolved_dir)) {
        return strdup(""); // Directory path is invalid or inaccessible
    }

    // Normalize and validate the full file path
    char resolved_file[PATH_MAX];
    if (!realpath(full_path, resolved_file)) {
        return strdup(""); // File path is invalid or inaccessible
    }

    // Ensure the file is within the specified directory
    if (strncmp(resolved_file, resolved_dir, strlen(resolved_dir)) != 0) {
        return strdup(""); // File is outside the allowed directory
    }

    // Open the file for reading
    FILE *file = fopen(resolved_file, "r");
    if (!file) {
        return strdup(""); // File could not be opened
    }

    // Determine the file size
    if (fseek(file, 0, SEEK_END) != 0) {
        fclose(file);
        return strdup(""); // Failed to seek to the end of the file
    }
    long file_size = ftell(file);
    if (file_size < 0) {
        fclose(file);
        return strdup(""); // Failed to determine file size
    }
    rewind(file);

    // Allocate memory for the file content
    char *content = (char *)malloc(file_size + 1);
    if (!content) {
        fclose(file);
        return strdup(""); // Memory allocation failed
    }

    // Read the file content
    size_t read_size = fread(content, 1, file_size, file);
    if (read_size != (size_t)file_size) {
        free(content);
        fclose(file);
        return strdup(""); // Failed to read the entire file
    }
    content[file_size] = '\0'; // Null-terminate the string

    // Close the file and return the content
    fclose(file);
    return content;
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
