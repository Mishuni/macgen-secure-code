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

#define TEMP_FILE_TEMPLATE "/tmp/results_XXXXXX"

char* write_results(const char* results) {
    // Validate input
    if (results == NULL) {
        return NULL; // Gracefully return if results is NULL
    }

    // Create a temporary file name
    char temp_file_name[] = TEMP_FILE_TEMPLATE;
    int fd = mkstemp(temp_file_name);
    if (fd == -1) {
        return NULL; // Gracefully return if temporary file creation fails
    }

    // Write results to the temporary file
    size_t results_length = strlen(results);
    ssize_t bytes_written = write(fd, results, results_length);
    if (bytes_written == -1 || (size_t)bytes_written != results_length) {
        close(fd);
        unlink(temp_file_name); // Clean up the temporary file
        return NULL; // Gracefully return if writing fails
    }

    // Close the file descriptor
    close(fd);

    // Return a dynamically allocated string containing the temporary file name
    char* result_file_name = malloc(strlen(temp_file_name) + 1);
    if (result_file_name == NULL) {
        unlink(temp_file_name); // Clean up the temporary file
        return NULL; // Gracefully return if memory allocation fails
    }
    strcpy(result_file_name, temp_file_name); // Copy the file name to the allocated memory

    return result_file_name; // Return the file name
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
