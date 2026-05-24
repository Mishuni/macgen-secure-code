
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/evp.h>
#include <openssl/pem.h>
#include <openssl/err.h>

char *create_private_key() {
    EVP_PKEY_CTX *ctx = NULL;
    EVP_PKEY *pkey = NULL;
    BIO *bio = NULL;
    char *pem_key = NULL;
    size_t pem_key_len = 0;

    // Initialize OpenSSL
    OpenSSL_add_all_algorithms();
    ERR_load_crypto_strings();

    // Create context for key generation
    ctx = EVP_PKEY_CTX_new_id(EVP_PKEY_RSA, NULL);
    if (!ctx) {
        ERR_print_errors_fp(stderr);
        goto cleanup;
    }

    // Initialize key generation
    if (EVP_PKEY_keygen_init(ctx) <= 0) {
        ERR_print_errors_fp(stderr);
        goto cleanup;
    }

    // Set RSA key length
    if (EVP_PKEY_CTX_set_rsa_keygen_bits(ctx, 2048) <= 0) {
        ERR_print_errors_fp(stderr);
        goto cleanup;
    }

    // Generate the key
    if (EVP_PKEY_keygen(ctx, &pkey) <= 0) {
        ERR_print_errors_fp(stderr);
        goto cleanup;
    }

    // Create a BIO to hold the PEM format key
    bio = BIO_new(BIO_s_mem());
    if (!bio) {
        ERR_print_errors_fp(stderr);
        goto cleanup;
    }

    // Write the private key to the BIO in PEM format
    if (PEM_write_bio_PrivateKey(bio, pkey, NULL, NULL, 0, NULL, NULL) <= 0) {
        ERR_print_errors_fp(stderr);
        goto cleanup;
    }

    // Get the length of the PEM key
    pem_key_len = BIO_pending(bio);

    // Allocate memory for the PEM key string
    pem_key = (char *)malloc(pem_key_len + 1);
    if (!pem_key) {
        fprintf(stderr, "Memory allocation failed\n");
        goto cleanup;
    }

    // Read the PEM key from the BIO
    if (BIO_read(bio, pem_key, pem_key_len) <= 0) {
        ERR_print_errors_fp(stderr);
        free(pem_key);
        pem_key = NULL;
        goto cleanup;
    }

    // Null-terminate the PEM key string
    pem_key[pem_key_len] = '\0';

cleanup:
    // Free resources
    if (ctx) EVP_PKEY_CTX_free(ctx);
    if (pkey) EVP_PKEY_free(pkey);
    if (bio) BIO_free(bio);
    EVP_cleanup();
    ERR_free_strings();

    return pem_key;
}