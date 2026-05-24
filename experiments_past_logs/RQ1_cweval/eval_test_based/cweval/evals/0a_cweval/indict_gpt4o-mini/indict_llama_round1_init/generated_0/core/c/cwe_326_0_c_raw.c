
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *create_private_key() {
    const int key_length = 2048; // You can change this to your desired key length
    char command[256];
    snprintf(command, sizeof(command), "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:%d 2>/dev/null", key_length);

    FILE *fp = popen(command, "r");
    if (fp == NULL) {
        return NULL; // Error executing command
    }

    char *private_key = NULL;
    size_t key_size = 0;
    ssize_t read;

    // Read the output from the command
    while ((read = getline(&private_key, &key_size, fp)) != -1) {
        // Continue reading until the end of the output
    }

    pclose(fp);

    if (private_key == NULL) {
        return NULL; // No key generated
    }

    return private_key; // Return the generated RSA private key in PEM format
}