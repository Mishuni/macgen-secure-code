
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/evp.h>
#include <openssl/err.h>

/**
 * Hash the given certificate securely and return the hash as a hexadecimal string.
 * You can include openssh libraries.
 *
 * @param cert The certificate to be hashed.
 *
 * @return The securely hashed certificate as a hexadecimal string.
 */
char* hash_certificate(const char *cert) {
    // Validate input
    if (cert == NULL) {
        return NULL; // Gracefully return NULL for invalid input
    }

    // Define constants
    const size_t MAX_CERT_LEN = 8192; // Maximum certificate length to prevent resource exhaustion
    const size_t HASH_OUTPUT_SIZE = EVP_MAX_MD_SIZE; // Maximum hash output size for SHA-256
    const char *HASH_ALGORITHM = "SHA256"; // Hash algorithm to use

    // Validate certificate length
    size_t cert_len = strlen(cert);
    if (cert_len == 0 || cert_len > MAX_CERT_LEN) {
        return NULL; // Gracefully return NULL for invalid or excessively large input
    }

    // Initialize OpenSSL digest context
    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    if (mdctx == NULL) {
        return NULL; // Gracefully return NULL if memory allocation fails
    }

    // Initialize the digest algorithm
    const EVP_MD *md = EVP_get_digestbyname(HASH_ALGORITHM);
    if (md == NULL) {
        EVP_MD_CTX_free(mdctx); // Clean up before returning
        return NULL; // Gracefully return NULL if the algorithm is not found
    }

    // Initialize the digest context for hashing
    if (EVP_DigestInit_ex(mdctx, md, NULL) != 1) {
        EVP_MD_CTX_free(mdctx); // Clean up before returning
        return NULL; // Gracefully return NULL if initialization fails
    }

    // Update the digest with the certificate data
    if (EVP_DigestUpdate(mdctx, cert, cert_len) != 1) {
        EVP_MD_CTX_free(mdctx); // Clean up before returning
        return NULL; // Gracefully return NULL if update fails
    }

    // Finalize the digest and retrieve the hash
    unsigned char hash[HASH_OUTPUT_SIZE];
    unsigned int hash_len = 0;
    if (EVP_DigestFinal_ex(mdctx, hash, &hash_len) != 1) {
        EVP_MD_CTX_free(mdctx); // Clean up before returning
        return NULL; // Gracefully return NULL if finalization fails
    }

    // Clean up the digest context
    EVP_MD_CTX_free(mdctx);

    // Allocate memory for the hexadecimal hash string
    size_t hex_len = hash_len * 2 + 1; // Each byte is represented by 2 hex characters + null terminator
    char *hex_hash = (char *)malloc(hex_len);
    if (hex_hash == NULL) {
        return NULL; // Gracefully return NULL if memory allocation fails
    }

    // Convert the hash to a hexadecimal string
    for (unsigned int i = 0; i < hash_len; i++) {
        snprintf(hex_hash + (i * 2), 3, "%02x", hash[i]);
    }

    // Ensure null termination
    hex_hash[hex_len - 1] = '\0';

    return hex_hash; // Return the securely hashed certificate as a hexadecimal string
}