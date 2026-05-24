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

#include <stdlib.h>     /* malloc, free */
#include <stdio.h>      /* fopen, fread, fclose */
#include <string.h>     /* strlen */
#include <errno.h>      /* errno */
#include <stdbool.h>    /* bool */

#define BUFFER_SIZE 4096

char *read_file_from_dir(const char *filename, const char *dir_path) {
    if (filename == NULL || dir_path == NULL) {
        return strdup(""); // Return empty string if input is invalid
    }

    // Validate filename for unsafe characters (e.g., path traversal)
    if (strstr(filename, "..") != NULL || strstr(filename, "/") != NULL || strstr(filename, "\\") != NULL) {
        return strdup(""); // Return empty string if filename is unsafe
    }

    // Construct the full file path
    size_t path_len = strlen(dir_path) + strlen(filename) + 2; // +2 for '/' and '\0'
    char *full_path = malloc(path_len);
    if (full_path == NULL) {
        return strdup(""); // Return empty string if memory allocation fails
    }
    snprintf(full_path, path_len, "%s/%s", dir_path, filename);

    // Open the file
    FILE *file = fopen(full_path, "rb");
    free(full_path); // Free the full_path after use
    if (file == NULL) {
        return strdup(""); // Return empty string if file cannot be opened
    }

    // Read the file content
    char *buffer = malloc(BUFFER_SIZE);
    if (buffer == NULL) {
        fclose(file);
        return strdup(""); // Return empty string if memory allocation fails
    }

    size_t total_read = 0;
    size_t bytes_read;
    char *content = NULL;

    while ((bytes_read = fread(buffer, 1, BUFFER_SIZE, file)) > 0) {
        char *new_content = realloc(content, total_read + bytes_read + 1);
        if (new_content == NULL) {
            free(content);
            free(buffer);
            fclose(file);
            return strdup(""); // Return empty string if memory allocation fails
        }
        content = new_content;
        memcpy(content + total_read, buffer, bytes_read);
        total_read += bytes_read;
    }

    // Null-terminate the content
    if (content != NULL) {
        content[total_read] = '\0';
    }

    free(buffer);
    fclose(file);
    return content ? content : strdup(""); // Return content or empty string if read fails
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
