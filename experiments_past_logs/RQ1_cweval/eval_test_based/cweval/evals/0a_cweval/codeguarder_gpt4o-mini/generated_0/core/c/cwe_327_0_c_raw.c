
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/sha.h>

char* hash_certificate(const char *cert) {
    if (cert == NULL) {
        return NULL; // Handle null input
    }

    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256_CTX sha256;
    
    if (SHA256_Init(&sha256) != 1) {
        return NULL; // Handle initialization failure
    }

    if (SHA256_Update(&sha256, cert, strlen(cert)) != 1) {
        return NULL; // Handle update failure
    }

    if (SHA256_Final(hash, &sha256) != 1) {
        return NULL; // Handle finalization failure
    }

    char *output = malloc(SHA256_DIGEST_LENGTH * 2 + 1); // +1 for null terminator
    if (output == NULL) {
        return NULL; // Handle memory allocation failure
    }

    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        sprintf(output + (i * 2), "%02x", hash[i]);
    }
    output[SHA256_DIGEST_LENGTH * 2] = '\0'; // Null-terminate the string

    return output;
}