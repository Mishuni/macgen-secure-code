#include <openssl/sha.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

char* hash_certificate(const char *cert) {
    if (cert == NULL) {
        return NULL; // Ensure the pointer is not NULL before dereferencing
    }

    size_t cert_length = strlen(cert);
    if (cert_length == 0) {
        return NULL; // Handle empty certificate string
    }

    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256((const unsigned char*)cert, cert_length, hash); // No need to check return value

    // Allocate memory for the hexadecimal string
    char *hex_hash = malloc(SHA256_DIGEST_LENGTH * 2 + 1);
    if (hex_hash == NULL) {
        return NULL; // Handle memory allocation failure
    }

    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        snprintf(&hex_hash[i * 2], 3, "%02x", hash[i]); // Safe usage of snprintf
    }
    hex_hash[SHA256_DIGEST_LENGTH * 2] = '\0'; // Null-terminate the string

    return hex_hash; // Return the securely hashed certificate as a hexadecimal string
}