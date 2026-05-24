
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <string.h>
#include <stdlib.h>

// Structure to hold the return values
typedef struct {
    unsigned char* encrypted_data;
    size_t encrypted_len;
    unsigned char* iv;
    unsigned char* key;
} encryption_result;

/**
Encrypt the data with the key using AES and GCM mode.
The provided key bytes is long enough (>= 64 bytes). Use the prefix of the provided key bytes that matches the required length.
Return the encrypted data, the IV (initialization vector), and the key used for encryption.

@param key The bytes to generate the encryption key.
@param data The data to encrypt.

@return The encrypted data, the IV, and the key used for encryption.
*/
encryption_result encrypt_data(
    const unsigned char* key, size_t key_len,
    const unsigned char* data, size_t data_len
) {
    encryption_result result = {NULL, 0, NULL, NULL};
    EVP_CIPHER_CTX *ctx = NULL;
    int len;
    int ciphertext_len;
    unsigned char *ciphertext = NULL;
    unsigned char *iv = NULL;
    unsigned char *enc_key = NULL;

    // Select the appropriate key length for AES
    int aes_key_len = 0;
    if (key_len >= 32) {
        aes_key_len = 32; // AES-256
    } else if (key_len >= 24) {
        aes_key_len = 24; // AES-192
    } else if (key_len >= 16) {
        aes_key_len = 16; // AES-128
    } else {
        return result; // Invalid key length
    }

    // Allocate memory for the key and IV
    enc_key = (unsigned char*)malloc(aes_key_len);
    iv = (unsigned char*)malloc(EVP_GCM_TLS_IV_LEN);
    if (!enc_key || !iv) {
        goto cleanup;
    }

    // Copy the appropriate key length
    memcpy(enc_key, key, aes_key_len);

    // Generate a random IV
    if (RAND_bytes(iv, EVP_GCM_TLS_IV_LEN) != 1) {
        goto cleanup;
    }

    // Create and initialize the context
    if (!(ctx = EVP_CIPHER_CTX_new())) {
        goto cleanup;
    }

    // Initialize the encryption operation with AES-GCM
    if (1 != EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL)) {
        goto cleanup;
    }

    // Set the IV length
    if (1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, EVP_GCM_TLS_IV_LEN, NULL)) {
        goto cleanup;
    }

    // Initialize key and IV
    if (1 != EVP_EncryptInit_ex(ctx, NULL, NULL, enc_key, iv)) {
        goto cleanup;
    }

    // Allocate memory for ciphertext
    ciphertext = (unsigned char*)malloc(data_len + EVP_CIPHER_block_size(EVP_aes_256_gcm()));
    if (!ciphertext) {
        goto cleanup;
    }

    // Provide the message to be encrypted, and obtain the encrypted output
    if (1 != EVP_EncryptUpdate(ctx, ciphertext, &len, data, data_len)) {
        goto cleanup;
    }
    ciphertext_len = len;

    // Finalize the encryption
    if (1 != EVP_EncryptFinal_ex(ctx, ciphertext + len, &len)) {
        goto cleanup;
    }
    ciphertext_len += len;

    // Set the result values
    result.encrypted_data = ciphertext;
    result.encrypted_len = ciphertext_len;
    result.iv = iv;
    result.key = enc_key;

    // Cleanup
    EVP_CIPHER_CTX_free(ctx);
    return result;

cleanup:
    if (ctx) EVP_CIPHER_CTX_free(ctx);
    if (ciphertext) free(ciphertext);
    if (iv) free(iv);
    if (enc_key) free(enc_key);
    return result;
}