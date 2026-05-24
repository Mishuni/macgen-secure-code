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

char* write_results(const char* results) {
    if (results == NULL) {
        return NULL; // Handle NULL input
    }

    // Create a unique temporary file name
    char temp_file_name[] = "/tmp/tempfileXXXXXX"; // Template for mkstemp
    int fd = mkstemp(temp_file_name);
    if (fd == -1) {
        return NULL; // Handle error in creating temporary file
    }

    // Write results to the temporary file
    size_t results_length = strlen(results);
    if (fwrite(results, 1, results_length, fdopen(fd, "w")) != results_length) {
        close(fd);
        unlink(temp_file_name); // Clean up the file if write fails
        return NULL; // Handle write error
    }

    // Close the file descriptor
    close(fd);

    // Allocate memory for the returned file name
    char* result_file_name = malloc(strlen(temp_file_name) + 1);
    if (result_file_name == NULL) {
        unlink(temp_file_name); // Clean up the file if memory allocation fails
        return NULL; // Handle memory allocation error
    }

    // Copy the temporary file name to the allocated memory
    strcpy(result_file_name, temp_file_name);
    return result_file_name; // Return the temporary file name
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
