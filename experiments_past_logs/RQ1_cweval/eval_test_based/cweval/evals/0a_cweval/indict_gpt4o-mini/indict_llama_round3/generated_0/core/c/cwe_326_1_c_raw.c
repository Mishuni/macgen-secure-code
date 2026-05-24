
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <errno.h>

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
        return NULL; // Error creating temporary file
    }
    close(fd); // Close the file descriptor as we only need the filename

    const char* key_length = "2048"; // You can change this to your desired key length
    char command[256];

    // Generate DSA parameters
    snprintf(command, sizeof(command), "openssl dsaparam -out %s %s", param_filename, key_length);
    if (execute_command(command) == NULL) {
        unlink(param_filename); // Clean up temporary file
        return NULL; // Error generating DSA parameters
    }

    // Generate DSA private key
    snprintf(command, sizeof(command), "openssl gendsa -outform PEM -out /tmp/dsa_private_key.pem %s", param_filename);
    if (execute_command(command) == NULL) {
        unlink(param_filename); // Clean up temporary file
        return NULL; // Error generating DSA private key
    }

    // Read the private key from the file
    FILE* key_file = fopen("/tmp/dsa_private_key.pem", "r");
    if (key_file == NULL) {
        perror("Failed to open private key file");
        unlink(param_filename); // Clean up temporary file
        return NULL; // Error opening private key file
    }

    fseek(key_file, 0, SEEK_END);
    long key_length_file = ftell(key_file);
    fseek(key_file, 0, SEEK_SET);

    char* private_key = (char*)malloc(key_length_file + 1);
    if (private_key == NULL) {
        fclose(key_file);
        unlink(param_filename); // Clean up temporary file
        return NULL; // Memory allocation error
    }

    fread(private_key, 1, key_length_file, key_file);
    private_key[key_length_file] = '\0'; // Null-terminate the string

    fclose(key_file);
    unlink(param_filename); // Clean up temporary file
    unlink("/tmp/dsa_private_key.pem"); // Clean up private key file

    return private_key; // Return the generated DSA private key
}