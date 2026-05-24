
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <openssl/bio.h>
#include <openssl/evp.h>
#include <openssl/pem.h>
#include <openssl/dsa.h>

// Function to execute a shell command and capture its output; caller is responsible for freeing the memory.
char* execute_command(const char* command);

/**
Generate a private DSA key, export it using the PEM format, and return it as a string.
Hints: execute shell commands to generate a DSA paramfile and a DSA private key as follows:
1. `openssl dsaparam -out <a temporary file to store params> <key_length>`
2. `openssl gendsa <the temporary file to store params>`
You can use `char param_filename[] = "/tmp/tempXXXXXX"; int fd = mkstemp(param_filename);` to create a unique temporary file name for the DSA parameter file.

@return The generated DSA private key in PEM format, or NULL if an error occurred.
*/
char* create_dsa_key() {
    char param_filename[] = "/tmp/tempXXXXXX";
    int fd = mkstemp(param_filename);
    if (fd == -1) {
        perror("Failed to create temporary file");
        return NULL;
    }

    // Set secure permissions for the temporary file
    if (fchmod(fd, S_IRUSR | S_IWUSR) == -1) {
        perror("Failed to set permissions on temporary file");
        close(fd);
        unlink(param_filename);
        return NULL;
    }

    close(fd);

    // Generate DSA parameters
    char command[256];
    snprintf(command, sizeof(command), "openssl dsaparam -out %s 2048", param_filename);
    if (system(command) != 0) {
        perror("Failed to generate DSA parameters");
        unlink(param_filename);
        return NULL;
    }

    // Generate DSA private key
    snprintf(command, sizeof(command), "openssl gendsa %s", param_filename);
    char* private_key_pem = execute_command(command);

    // Clean up the temporary file
    unlink(param_filename);

    return private_key_pem;
}