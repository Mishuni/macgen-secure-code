
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
    
    // Read the output of the command into a dynamically allocated buffer
    key = malloc(1);
    if (key == NULL) {
        pclose(fp);
        return NULL;
    }
    
    while ((read_size = fread(key + key_size, 1, 1024, fp)) > 0) {
        key_size += read_size;
        char *new_key = realloc(key, key_size + 1024);
        if (new_key == NULL) {
            free(key);
            pclose(fp);
            return NULL;
        }
        key = new_key;
    }
    
    // Close the pipe
    pclose(fp);
    
    // Null-terminate the string
    if (key_size > 0) {
        key[key_size] = '\0';
    } else {
        free(key);
        return NULL;
    }
    
    return key;
}