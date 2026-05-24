
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/sha.h>

#define HASH_OUTPUT_SIZE (SHA256_DIGEST_LENGTH * 2 + 1) // SHA256 produces 32 bytes, each byte is represented by 2 hex characters + null terminator

/**
Hash the given certificate securely and return the hash as a hexadecimal string.

@param cert The certificate to be hashed.

@return The securely hashed certificate as a hexadecimal string.
*/
char* hash_certificate(const char *cert) {
    if (cert == NULL) {
        return NULL; // Gracefully handle null input
    }

    size_t cert_length = strlen(cert);
    if (cert_length == 0) {
        return NULL; // Gracefully handle empty certificate
    }

    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256((unsigned char*)cert, cert_length, hash); // Hash the certificate

    char *hash_hex = malloc(HASH_OUTPUT_SIZE);
    if (hash_hex == NULL) {
        return NULL; // Gracefully handle memory allocation failure
    }

    for (size_t i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        sprintf(&hash_hex[i * 2], "%02x", hash[i]); // Convert to hexadecimal
    }

    hash_hex[HASH_OUTPUT_SIZE - 1] = '\0'; // Null-terminate the string
    return hash_hex; // Return the hexadecimal string
}