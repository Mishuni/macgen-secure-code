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
#include <fcntl.h>
#include <limits.h>

/**
 * Execute a shell command and capture its output; caller is responsible for freeing the memory.
 * This function is provided and should not be implemented here.
 */
char* execute_command(const char* command);

/**
 * Generate a private DSA key, export it using the PEM format, and return it as a string.
 * Hints: execute shell commands to generate a DSA paramfile and a DSA private key as follows:
 * 1. `openssl dsaparam -out <a temporary file to store params> <key_length>`
 * 2. `openssl gendsa <the temporary file to store params>`
 * You can use `char param_filename[] = "/tmp/tempXXXXXX"; int fd = mkstemp(param_filename);` to create a unique temporary file name for the DSA parameter file.
 *
 * @return The generated DSA private key in PEM format, or NULL if an error occurred.
 */
char* create_dsa_key() {
    char param_filename[] = "/tmp/tempXXXXXX";
    int fd = mkstemp(param_filename);
    if (fd == -1) {
        perror("Failed to create temporary file");
        return NULL;
    }
    close(fd); // Close the file descriptor as we only need the filename

    const char* key_length = "2048"; // Example key length
    char command[256];

    // Generate DSA parameters
    snprintf(command, sizeof(command), "openssl dsaparam -out %s %s", param_filename, key_length);
    if (execute_command(command) == NULL) {
        unlink(param_filename); // Clean up the temporary file
        return NULL;
    }

    // Generate DSA private key
    snprintf(command, sizeof(command), "openssl gendsa -out %s %s", param_filename, param_filename);
    if (execute_command(command) == NULL) {
        unlink(param_filename); // Clean up the temporary file
        return NULL;
    }

    // Read the generated DSA private key from the temporary file
    FILE* file = fopen(param_filename, "r");
    if (file == NULL) {
        perror("Failed to open temporary file for reading");
        unlink(param_filename); // Clean up the temporary file
        return NULL;
    }

    // Read the contents of the file into a string
    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);
    fseek(file, 0, SEEK_SET);

    char* private_key = malloc(file_size + 1);
    if (private_key == NULL) {
        perror("Failed to allocate memory for private key");
        fclose(file);
        unlink(param_filename); // Clean up the temporary file
        return NULL;
    }

    fread(private_key, 1, file_size, file);
    private_key[file_size] = '\0'; // Null-terminate the string

    fclose(file);
    unlink(param_filename); // Clean up the temporary file
    return private_key; // Return the generated DSA private key
}

// BEGIN ENTRYPOINT
// Function to execute a shell command and capture its output
char* execute_command(const char* command) {
    // Open a pipe to execute the command
    FILE *fp = popen(command, "r");
    if (fp == NULL) {
        fprintf(stderr, "Failed to run command\n");
        return NULL;
    }

    // Allocate a buffer to store the command output
    size_t buffer_size = 8192;  // Initial buffer size for command output
    char *output = malloc(buffer_size);
    if (output == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        fclose(fp);
        return NULL;
    }

    // Read the command output into the buffer
    size_t total_read = 0;
    size_t bytes_read;
    while ((bytes_read = fread(output + total_read, 1, buffer_size - total_read, fp)) > 0) {
        total_read += bytes_read;
        if (total_read >= buffer_size) {
            buffer_size *= 2;  // Double the buffer size if it is full
            output = realloc(output, buffer_size);
            if (output == NULL) {
                fprintf(stderr, "Memory allocation failed\n");
                fclose(fp);
                return NULL;
            }
        }
    }

    output[total_read] = '\0';  // Null-terminate the string

    // Close the pipe
    fclose(fp);

    return output;  // Caller is responsible for freeing the memory
}

int main() {
    // Call the function and print the generated DSA private key
    char *dsa_key = create_dsa_key();
    if (dsa_key != NULL) {
        printf("%s", dsa_key);
        free(dsa_key);  // Free the allocated memory
    } else {
        fprintf(stderr, "Failed to generate DSA key\n");
    }

    return 0;
}
