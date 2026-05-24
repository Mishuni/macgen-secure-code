
#include <openssl/evp.h>
#include <openssl/sha.h>
#include <string.h>
#include <stdlib.h>

char* hash_certificate(const char *cert) {
    if (cert == NULL) {
        return NULL; // Handle NULL input
    }

    size_t cert_length = strlen(cert);
    if (cert_length == 0) {
        return NULL; // Handle empty input
    }

    unsigned char hash[SHA256_DIGEST_LENGTH];
    char *hex_hash = (char *)malloc(SHA256_DIGEST_LENGTH * 2 + 1);
    if (!hex_hash) {
        return NULL; // Memory allocation failed
    }

    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    if (mdctx == NULL) {
        free(hex_hash);
        return NULL;
    }

    if (EVP_DigestInit_ex(mdctx, EVP_sha256(), NULL) != 1) {
        EVP_MD_CTX_free(mdctx);
        free(hex_hash);
        return NULL;
    }

    if (EVP_DigestUpdate(mdctx, cert, cert_length) != 1) {
        EVP_MD_CTX_free(mdctx);
        free(hex_hash);
        return NULL;
    }

    if (EVP_DigestFinal_ex(mdctx, hash, NULL) != 1) {
        EVP_MD_CTX_free(mdctx);
        free(hex_hash);
        return NULL;
    }

    EVP_MD_CTX_free(mdctx);

    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        sprintf(&hex_hash[i * 2], "%02x", hash[i]);
    }

    hex_hash[SHA256_DIGEST_LENGTH * 2] = '\0'; // Null-terminate the string

    return hex_hash;
}