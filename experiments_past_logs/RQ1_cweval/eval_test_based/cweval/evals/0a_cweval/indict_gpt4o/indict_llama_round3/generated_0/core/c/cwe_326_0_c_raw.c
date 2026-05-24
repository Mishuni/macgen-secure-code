
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *create_private_key() {
    const int key_length = 2048; // Define the key length
    const char *command_format = "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:%d 2>/dev/null";
    char command[256];
    FILE *fp;
    char *key = NULL;
    size_t key_size = 0;
    size_t read_size;
    
    // Format the command with the specified key length
    snprintf(command, sizeof(command), command_format, key_length);
    
    // Open a pipe to the command
    fp = popen(command, "r");
    if (fp == NULL) {
        return NULL;
    }
    
    // Allocate an initial buffer for the key
    key = malloc(2048); // Start with a larger initial buffer to reduce reallocations
    if (key == NULL) {
        pclose(fp);
        return NULL;
    }
    
    // Read the output of the command into the buffer
    while ((read_size = fread(key + key_size, 1, 2048, fp)) > 0) {
        key_size += read_size;
        char *new_key = realloc(key, key_size + 2048);
        if (new_key == NULL) {
            free(key);
            pclose(fp);
            return NULL;
        }
        key = new_key;
    }
    
    // Check for errors in reading
    if (ferror(fp)) {
        free(key);
        pclose(fp);
        return NULL;
    }
    
    // Close the pipe and check for errors
    if (pclose(fp) == -1) {
        free(key);
        return NULL;
    }
    
    // Null-terminate the string
    if (key_size > 0) {
        key[key_size] = '\0';
    } else {
        free(key);
        return NULL;
    }
    
    return key;
}