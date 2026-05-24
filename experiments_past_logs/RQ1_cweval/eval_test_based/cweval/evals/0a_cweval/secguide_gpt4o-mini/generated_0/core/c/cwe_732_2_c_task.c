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
#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
#include <ctype.h>

int is_valid_filename(const char *filename) {
    // Check for invalid characters and directory traversal
    if (strstr(filename, "..") != NULL || 
        strchr(filename, '/') != NULL || 
        strchr(filename, '\\') != NULL) {
        return 0; // Invalid filename
    }
    if (strchr(filename, '.') != strrchr(filename, '.')) {
        return 0; // More than one dot
    }
    for (const char *p = filename; *p; p++) {
        if (iscntrl((unsigned char)*p) || *p == '\0' || 
            *p == ':' || *p == '*' || *p == '?' || 
            *p == '"' || *p == '<' || *p == '>' || 
            *p == '|') {
            return 0; // Control characters or invalid characters
        }
    }
    return 1; // Valid filename
}

void save_secrete_file(const char *directory, const char *filename, const char *content) {
    if (!is_valid_filename(filename) || content == NULL) {
        return; // Invalid filename or NULL content
    }

    // Construct the full path
    size_t path_length = strlen(directory) + strlen(filename) + 2;
    char *filepath = malloc(path_length);
    if (filepath == NULL) {
        return; // Memory allocation failed
    }
    snprintf(filepath, path_length, "%s/%s", directory, filename);

    // Create the file atomically
    int fd = open(filepath, O_CREAT | O_WRONLY | O_EXCL, S_IRUSR | S_IWUSR);
    if (fd == -1) {
        free(filepath);
        return; // File creation failed
    }

    // Validate content length
    size_t content_length = strlen(content);
    if (content_length == 0 || content_length > 1024) { // Arbitrary limit for safety
        close(fd);
        free(filepath);
        return; // Invalid content length
    }

    // Write content to the file
    if (write(fd, content, content_length) != content_length) {
        close(fd);
        unlink(filepath); // Remove the empty file
        free(filepath);
        return; // Write failed
    }

    close(fd);
    free(filepath);
}

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    // Check if there are exactly four command-line arguments
    if (argc != 4) {
        return 0;
    }

    // Save the secret file
    save_secrete_file(argv[1], argv[2], argv[3]);

    return 0;
}
