#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/evp.h>
#include <openssl/pem.h>
#include <openssl/rand.h>
#include <openssl/err.h>

char *create_private_key() {
    EVP_PKEY *pkey = NULL;
    BIO *bio = NULL;
    char *key = NULL;
    size_t key_len = 0;
    BIGNUM *bn = NULL;
    RSA *rsa = NULL;

    // Initialize OpenSSL algorithms
    OpenSSL_add_all_algorithms();
    ERR_load_crypto_strings();

    // Generate the RSA private key
    pkey = EVP_PKEY_new();
    if (!pkey) {
        goto cleanup;
    }

    rsa = RSA_new();
    if (!rsa) {
        goto cleanup;
    }

    bn = BN_new();
    if (!bn || !BN_set_word(bn, RSA_F4)) {
        goto cleanup;
    }

    if (!RSA_generate_key_ex(rsa, 2048, bn, NULL)) {
        goto cleanup;
    }

    if (!EVP_PKEY_assign_RSA(pkey, rsa)) {
        goto cleanup;
    }
    rsa = NULL; // pkey owns the RSA structure now

    // Create a memory BIO to hold the key
    bio = BIO_new(BIO_s_mem());
    if (!bio) {
        goto cleanup;
    }

    // Encrypt the private key with a passphrase
    const EVP_CIPHER *cipher = EVP_aes_256_cbc();
    unsigned char passphrase[] = "securepassphrase"; // Use a secure method to handle passphrases

    if (!PEM_write_bio_PrivateKey(bio, pkey, cipher, passphrase, strlen((char *)passphrase), NULL, NULL)) {
        goto cleanup;
    }

    // Get the length of the key
    key_len = BIO_pending(bio);

    // Allocate memory for the key
    key = (char *)malloc(key_len + 1);
    if (!key) {
        goto cleanup;
    }

    // Read the key from the BIO
    if (BIO_read(bio, key, key_len) <= 0) {
        free(key);
        key = NULL;
        goto cleanup;
    }

    key[key_len] = '\0'; // Null-terminate the string

cleanup:
    if (bn) BN_free(bn);
    if (rsa) RSA_free(rsa);
    if (bio) BIO_free(bio);
    if (pkey) EVP_PKEY_free(pkey);

    // Cleanse the passphrase from memory
    OPENSSL_cleanse(passphrase, sizeof(passphrase));

    // Cleanup OpenSSL
    EVP_cleanup();
    ERR_free_strings();

    return key;
}