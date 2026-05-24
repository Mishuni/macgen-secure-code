#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/sha.h>

char* hash_certificate(const char *cert) {
    if (!cert || strlen(cert) == 0) return NULL;

    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256_CTX sha256;

    if (SHA256_Init(&sha256) != 1) {
        return NULL;
    }

    if (SHA256_Update(&sha256, cert, strlen(cert)) != 1) {
        return NULL;
    }

    if (SHA256_Final(hash, &sha256) != 1) {
        return NULL;
    }

    char *output = malloc(SHA256_DIGEST_LENGTH * 2 + 1);
    if (!output) {
        return NULL;
    }

    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        snprintf(output + (i * 2), 3, "%02x", hash[i]);
    }

    output[SHA256_DIGEST_LENGTH * 2] = '\0';
    return output;
}