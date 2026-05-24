#include <openssl/evp.h>
#include <openssl/sha.h>
#include <string.h>
#include <stdlib.h>
#include <openssl/err.h>

char* hash_certificate(const char *cert, size_t cert_len) {
    if (cert == NULL || cert_len == 0) {
        return NULL;
    }

    // Create a context for the hash function
    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    if (mdctx == NULL) {
        return NULL;
    }

    // Initialize the context with the SHA-256 algorithm
    if (EVP_DigestInit_ex(mdctx, EVP_sha256(), NULL) != 1) {
        EVP_MD_CTX_free(mdctx);
        return NULL;
    }

    // Update the context with the certificate data
    if (EVP_DigestUpdate(mdctx, cert, cert_len) != 1) {
        EVP_MD_CTX_free(mdctx);
        return NULL;
    }

    // Finalize the hash and retrieve the result
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hash_len;
    if (EVP_DigestFinal_ex(mdctx, hash, &hash_len) != 1) {
        EVP_MD_CTX_free(mdctx);
        return NULL;
    }

    // Clean up the context
    EVP_MD_CTX_free(mdctx);

    // Check for potential overflow in allocation size
    if (hash_len > (SIZE_MAX - 1) / 2) {
        return NULL;
    }

    // Convert the hash to a hexadecimal string
    char *hex_hash = (char *)malloc(hash_len * 2 + 1);
    if (hex_hash == NULL) {
        return NULL;
    }

    for (unsigned int i = 0; i < hash_len; i++) {
        if (snprintf(hex_hash + (i * 2), 3, "%02x", hash[i]) < 0) {
            free(hex_hash);
            return NULL;
        }
    }
    hex_hash[hash_len * 2] = '\0';

    return hex_hash;
}