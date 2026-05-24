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
#include <errno.h>

#define MAX_FILENAME_LENGTH 255
#define MAX_PATH_LENGTH 512
#define MAX_FILE_SIZE 1048576 // 1 MB limit for file size

char *read_file_from_dir(const char *filename, const char *dir_path) {
    // Validate filename: must not contain directory separators, "..", or exceed max length
    if (strchr(filename, '/') || strchr(filename, '\\') || strstr(filename, "..") || strlen(filename) > MAX_FILENAME_LENGTH) {
        return NULL; // Return NULL if invalid
    }

    // Validate dir_path: must not contain invalid characters or exceed max length
    if (strlen(dir_path) > MAX_PATH_LENGTH) {
        return NULL; // Return NULL if dir_path is too long
    }

    // Construct the full path
    char full_path[MAX_PATH_LENGTH];
    if (snprintf(full_path, sizeof(full_path), "%s/%s", dir_path, filename) >= sizeof(full_path)) {
        return NULL; // Return NULL if path construction exceeds buffer size
    }

    // Open the file
    FILE *file = fopen(full_path, "r");
    if (!file) {
        return NULL; // Return NULL if file cannot be opened
    }

    // Check the file size
    fseek(file, 0, SEEK_END);
    long length = ftell(file);
    if (length < 0 || length > MAX_FILE_SIZE) {
        fclose(file);
        return NULL; // Return NULL if file size is invalid or exceeds limit
    }
    fseek(file, 0, SEEK_SET);

    // Allocate memory for the content
    char *content = (char *)malloc(length + 1);
    if (!content) {
        fclose(file);
        return NULL; // Return NULL if memory allocation fails
    }

    // Read the content into the buffer
    size_t bytesRead = fread(content, 1, length, file);
    if (bytesRead < length) {
        free(content);
        fclose(file);
        return NULL; // Return NULL if fread fails to read the expected number of bytes
    }
    content[length] = '\0'; // Null-terminate the string

    if (fclose(file) != 0) {
        free(content); // Free content if fclose fails
        return NULL; // Return NULL if fclose fails
    }

    return content; // Return the content
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
