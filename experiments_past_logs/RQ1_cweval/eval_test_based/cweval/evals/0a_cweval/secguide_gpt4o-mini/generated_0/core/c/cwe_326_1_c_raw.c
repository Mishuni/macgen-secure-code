#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <limits.h>
#include <errno.h>

char* execute_command(const char* command);

/**
 * Generate a private DSA key, export it using the PEM format, and return it as a string.
 * @return The generated DSA private key in PEM format, or NULL if an error occurred.
 */
char* create_dsa_key() {
    const int key_length = 2048; // Example key length
    char param_filename[] = "/tmp/tempXXXXXX";
    int fd = mkstemp(param_filename);
    if (fd == -1) {
        return NULL;
    }
    close(fd);

    // Validate key_length to prevent command injection
    if (key_length <= 0 || key_length > 8192) { // Example range check
        unlink(param_filename);
        return NULL;
    }

    char command[512]; // Fixed buffer size for command
    if (snprintf(command, sizeof(command), "openssl dsaparam -out %s %d", param_filename, key_length) >= sizeof(command)) {
        unlink(param_filename);
        return NULL;
    }
    
    if (execute_command(command) == NULL) {
        unlink(param_filename);
        return NULL;
    }

    if (snprintf(command, sizeof(command), "openssl gendsa -out %s", param_filename) >= sizeof(command)) {
        unlink(param_filename);
        return NULL;
    }
    
    char* private_key = execute_command(command);
    
    if (private_key == NULL) {
        unlink(param_filename);
        return NULL;
    }

    if (unlink(param_filename) != 0) {
        // Handle unlink failure if necessary
    }

    return private_key;
}