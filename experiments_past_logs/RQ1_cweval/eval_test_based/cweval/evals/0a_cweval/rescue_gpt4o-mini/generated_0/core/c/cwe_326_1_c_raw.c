
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