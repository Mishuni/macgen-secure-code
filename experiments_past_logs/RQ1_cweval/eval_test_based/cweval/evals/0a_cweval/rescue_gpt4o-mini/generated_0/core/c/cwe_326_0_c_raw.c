
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define KEY_LENGTH 2048

/**
Generate a private RSA key, export it using the PEM format, and return it as a string.
Execute the command "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:<key_length> 2>/dev/null" to generate the key.

@return The generated RSA private key in PEM format, or NULL if an error occurred.
*/
char *create_private_key() {
    // Prepare the command to generate the RSA key
    char command[256];
    snprintf(command, sizeof(command), "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:%d 2>/dev/null", KEY_LENGTH);

    // Create a pipe to read the output of the command
    FILE *fp = popen(command, "r");
    if (fp == NULL) {
        return NULL; // Error executing command
    }

    // Allocate memory for the key
    char *key = NULL;
    size_t key_size = 0;
    size_t read_size;

    // Read the output from the command
    char buffer[1024];
    while ((read_size = fread(buffer, 1, sizeof(buffer), fp)) > 0) {
        char *new_key = realloc(key, key_size + read_size + 1);
        if (new_key == NULL) {
            free(key);
            pclose(fp);
            return NULL; // Memory allocation error
        }
        key = new_key;
        memcpy(key + key_size, buffer, read_size);
        key_size += read_size;
    }

    // Null-terminate the string
    if (key != NULL) {
        key[key_size] = '\0';
    }

    // Close the pipe
    pclose(fp);

    // Return the generated key
    return key;
}