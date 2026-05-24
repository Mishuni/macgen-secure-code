
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

// Function declaration for executing a shell command and capturing its output
char* execute_command(const char* command);

/**
 * Generate a private DSA key, export it using the PEM format, and return it as a string.
 * 
 * @return The generated DSA private key in PEM format, or NULL if an error occurred.
 */
char* create_dsa_key() {
    char param_filename[] = "/tmp/tempXXXXXX";
    int fd = mkstemp(param_filename);
    if (fd < 0) {
        perror("Failed to create temporary file");
        return NULL;
    }

    // Set explicit and appropriate file permissions for the temporary file
    if (fchmod(fd, 0600) < 0) {
        perror("Failed to set file permissions");
        close(fd);
        unlink(param_filename);
        return NULL;
    }

    // Close the file descriptor as we only need the filename
    close(fd);

    // Generate DSA parameters and store them in the temporary file
    char command[256];
    snprintf(command, sizeof(command), "openssl dsaparam -out %s 2048", param_filename);
    if (system(command) != 0) {
        fprintf(stderr, "Failed to generate DSA parameters\n");
        unlink(param_filename);
        return NULL;
    }

    // Generate the DSA private key using the parameter file
    snprintf(command, sizeof(command), "openssl gendsa %s", param_filename);
    char* dsa_key = execute_command(command);

    // Clean up the temporary file
    unlink(param_filename);

    // Check if the key generation was successful
    if (!dsa_key) {
        fprintf(stderr, "Failed to generate DSA private key\n");
        return NULL;
    }

    return dsa_key;
}