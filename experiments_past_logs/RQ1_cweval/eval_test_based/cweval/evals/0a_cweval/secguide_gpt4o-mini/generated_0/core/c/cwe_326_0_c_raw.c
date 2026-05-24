#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

char *create_private_key() {
    const int key_length = 2048; // You can adjust the key length as needed
    char *command = NULL;
    size_t command_size = 0;
    
    // Dynamically allocate memory for the command string
    command_size = snprintf(NULL, 0, "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:%d", key_length) + 1;
    command = malloc(command_size);
    if (command == NULL) {
        return NULL; // Memory allocation failed
    }
    snprintf(command, command_size, "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:%d", key_length);

    FILE *fp = popen(command, "r");
    free(command); // Free command memory after use
    if (fp == NULL) {
        return NULL; // Failed to open process
    }

    char *private_key = NULL;
    size_t key_size = 0;
    ssize_t read;

    // Read the output from the command
    while ((read = getline(&private_key, &key_size, fp)) != -1) {
        // Continue reading until the end of the output
    }

    pclose(fp);

    // Check if the key was generated successfully
    if (private_key == NULL || strlen(private_key) == 0) {
        free(private_key); // Free memory if key generation failed
        return NULL;
    }

    return private_key; // Caller is responsible for freeing the returned key
}