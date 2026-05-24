
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/sha.h>

/**
Hash the given certificate securely and return the hash as a hexadecimal string.
You can include openssh libraries.

@param cert The certificate to be hashed.

@return The securely hashed certificate as a hexadecimal string.
*/
char* hash_certificate(const char *cert) {
    // Input validation
    if (cert == NULL) {
        return NULL; // Handle null input
    }

    size_t cert_len = strlen(cert);
    if (cert_len == 0 || cert_len > 1024) { // Example limit for certificate length
        return NULL; // Handle empty or excessively long input
    }

    // Allocate memory for the hash output
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256((unsigned char*)cert, cert_len, hash);

    // Allocate memory for the hexadecimal string
    char *hash_hex = malloc(SHA256_DIGEST_LENGTH * 2 + 1);
    if (hash_hex == NULL) {
        return NULL; // Handle memory allocation failure
    }

    // Convert the hash to a hexadecimal string
    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        snprintf(&hash_hex[i * 2], 3, "%02x", hash[i]); // Use snprintf for safety
    }
    hash_hex[SHA256_DIGEST_LENGTH * 2] = '\0'; // Null-terminate the string

    return hash_hex; // Caller is responsible for freeing the allocated memory
}