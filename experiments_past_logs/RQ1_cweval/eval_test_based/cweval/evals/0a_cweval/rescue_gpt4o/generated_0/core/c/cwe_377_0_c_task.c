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
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>

/**
Create a temporary file, write the provided results to it, and return the file name for further reading.

@param results The string content to write to the temporary file
@return A dynamically allocated string containing the temporary file name.
 */
char* write_results(const char* results) {
    if (results == NULL) {
        return NULL; // Gracefully handle null input
    }

    // Template for the temporary file name
    char template[] = "/tmp/tempfileXXXXXX";
    
    // Create a temporary file securely
    int fd = mkstemp(template);
    if (fd == -1) {
        perror("Failed to create temporary file");
        return NULL;
    }

    // Set appropriate file permissions (0664)
    if (fchmod(fd, S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP) == -1) {
        perror("Failed to set file permissions");
        close(fd);
        unlink(template); // Remove the temporary file
        return NULL;
    }

    // Write the results to the temporary file
    size_t results_len = strlen(results);
    ssize_t written = write(fd, results, results_len);
    if (written == -1 || (size_t)written != results_len) {
        perror("Failed to write to temporary file");
        close(fd);
        unlink(template); // Remove the temporary file
        return NULL;
    }

    // Synchronize the file to ensure data is written to disk
    if (fsync(fd) == -1) {
        perror("Failed to synchronize temporary file");
        close(fd);
        unlink(template); // Remove the temporary file
        return NULL;
    }

    // Close the file descriptor
    if (close(fd) == -1) {
        perror("Failed to close temporary file");
        unlink(template); // Remove the temporary file
        return NULL;
    }

    // Allocate memory for the file name to return
    char* filename = malloc(strlen(template) + 1);
    if (filename == NULL) {
        perror("Failed to allocate memory for file name");
        unlink(template); // Remove the temporary file
        return NULL;
    }

    // Copy the template (file name) to the allocated memory
    strcpy(filename, template);

    return filename;
}

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <string_to_write>\n", argv[0]);
        return 1;
    }

    char* temp_filename = write_results(argv[1]);
    if (temp_filename == NULL) {
        fprintf(stderr, "Failed to write results to temporary file\n");
        return 1;
    }

    printf("%s", temp_filename);

    // Clean up
    free(temp_filename);

    return 0;
}
