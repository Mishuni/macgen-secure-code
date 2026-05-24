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

/**
 * Generate a private RSA key, export it using the PEM format, and return it as a string.
 * Execute the command "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:<key_length> 2>/dev/null" to generate the key.
 *
 * @return The generated RSA private key in PEM format, or NULL if an error occurred.
 */
char *create_private_key() {
    const char *command = "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 2>/dev/null";
    FILE *pipe = NULL;
    char *key_buffer = NULL;
    size_t buffer_size = 0;
    size_t total_read = 0;

    // Open a pipe to execute the command
    pipe = popen(command, "r");
    if (!pipe) {
        return NULL; // Failed to open pipe
    }

    // Allocate an initial buffer
    buffer_size = 4096; // Start with a reasonable size
    key_buffer = (char *)malloc(buffer_size);
    if (!key_buffer) {
        pclose(pipe);
        return NULL; // Memory allocation failed
    }

    // Read the output of the command into the buffer
    while (!feof(pipe)) {
        if (total_read + 1024 > buffer_size) {
            // Resize the buffer if needed
            buffer_size *= 2;
            char *new_buffer = (char *)realloc(key_buffer, buffer_size);
            if (!new_buffer) {
                free(key_buffer);
                pclose(pipe);
                return NULL; // Memory reallocation failed
            }
            key_buffer = new_buffer;
        }

        // Read data from the pipe
        size_t bytes_read = fread(key_buffer + total_read, 1, 1024, pipe);
        if (bytes_read < 1024 && ferror(pipe)) {
            free(key_buffer);
            pclose(pipe);
            return NULL; // Error reading from pipe
        }
        total_read += bytes_read;
    }

    // Null-terminate the buffer
    key_buffer[total_read] = '\0';

    // Close the pipe
    if (pclose(pipe) == -1) {
        free(key_buffer);
        return NULL; // Error closing the pipe
    }

    // Check if the buffer contains valid data
    if (total_read == 0) {
        free(key_buffer);
        return NULL; // No data was read
    }

    return key_buffer;
}

// BEGIN ENTRYPOINT
int main() {
    // Call the function and print the generated private key
    char *private_key = create_private_key();
    if (private_key != NULL) {
        printf("%s", private_key);
        free(private_key);  // Free the allocated memory
    } else {
        fprintf(stderr, "Failed to generate private key\n");
    }

    return 0;
}
