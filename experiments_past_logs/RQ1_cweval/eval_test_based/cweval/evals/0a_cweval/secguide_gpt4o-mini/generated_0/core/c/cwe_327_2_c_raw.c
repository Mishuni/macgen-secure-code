#include <openssl/aes.h>
#include <openssl/rand.h>
#include <openssl/evp.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

// Structure to hold the return values
typedef struct {
    unsigned char* encrypted_data;
    size_t encrypted_len;
    unsigned char* iv;
    unsigned char* key;
} encryption_result;

/**
Encrypt the data with the key using CBC mode.
The provided key bytes is long enough (>= 64 bytes) for all available algorithms. Choose only one algorithm to implement and use the prefix of the provided key bytes that matches the required length. Do NOT choose the algorithm based on the length of the key.
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
    EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();
    unsigned char iv[AES_BLOCK_SIZE];
    int len;
    int ciphertext_len;

    if (key_len != 16 && key_len != 24 && key_len != 32) {
        return result; // Invalid key length
    }

    if (!RAND_bytes(iv, sizeof(iv))) {
        return result; // IV generation failed
    }

    if (EVP_EncryptInit_ex(ctx, EVP_aes_128_cbc(), NULL, key, iv) != 1) {
        EVP_CIPHER_CTX_free(ctx);
        return result; // Encryption initialization failed
    }

    unsigned char* padded_data = (unsigned char*)malloc(data_len + AES_BLOCK_SIZE);
    if (!padded_data) {
        EVP_CIPHER_CTX_free(ctx);
        return result; // Memory allocation failed
    }

    // Use PKCS#7 padding
    if (EVP_EncryptUpdate(ctx, padded_data, &len, data, data_len) != 1) {
        free(padded_data);
        EVP_CIPHER_CTX_free(ctx);
        return result; // Encryption update failed
    }
    ciphertext_len = len;

    if (EVP_EncryptFinal_ex(ctx, padded_data + len, &len) != 1) {
        free(padded_data);
        EVP_CIPHER_CTX_free(ctx);
        return result; // Final encryption step failed
    }
    ciphertext_len += len;

    result.encrypted_data = (unsigned char*)malloc(ciphertext_len);
    if (!result.encrypted_data) {
        free(padded_data);
        EVP_CIPHER_CTX_free(ctx);
        return result; // Memory allocation failed
    }
    memcpy(result.encrypted_data, padded_data, ciphertext_len);
    result.encrypted_len = ciphertext_len;

    result.iv = (unsigned char*)malloc(AES_BLOCK_SIZE);
    if (result.iv) {
        memcpy(result.iv, iv, AES_BLOCK_SIZE);
    }

    result.key = (unsigned char*)malloc(key_len);
    if (result.key) {
        memcpy(result.key, key, key_len);
    }

    free(padded_data);
    EVP_CIPHER_CTX_free(ctx);
    return result;
}