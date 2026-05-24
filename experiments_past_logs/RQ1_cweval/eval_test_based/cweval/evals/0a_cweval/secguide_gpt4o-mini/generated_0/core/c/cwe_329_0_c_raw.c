#include <openssl/aes.h>
#include <openssl/rand.h>
#include <openssl/evp.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

// Structure to hold the return values
typedef struct {
    unsigned char* encrypted_data;
    size_t encrypted_len;
    unsigned char* iv;
    unsigned char* key;
} encryption_result;

/**
Encrypt the data with the key using AES and CBC mode.
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
    encryption_result result = {0};
    EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();
    unsigned char iv[AES_BLOCK_SIZE];
    int len;
    int ciphertext_len;

    // Validate key length
    if (key_len < 16 || (key_len != 16 && key_len != 24 && key_len != 32)) {
        return result; // Key length is insufficient or invalid
    }

    // Generate a random IV
    if (RAND_bytes(iv, sizeof(iv)) != 1) {
        return result; // IV generation failed
    }
    result.iv = (unsigned char*)malloc(AES_BLOCK_SIZE);
    if (!result.iv) {
        return result; // Memory allocation failed
    }
    memcpy(result.iv, iv, AES_BLOCK_SIZE);

    // Initialize encryption operation
    const EVP_CIPHER* cipher = (key_len == 16) ? EVP_aes_128_cbc() :
                               (key_len == 24) ? EVP_aes_192_cbc() :
                                                  EVP_aes_256_cbc();
    if (EVP_EncryptInit_ex(ctx, cipher, NULL, key, iv) != 1) {
        free(result.iv);
        return result; // Initialization failed
    }

    // Allocate memory for encrypted data
    result.encrypted_data = (unsigned char*)malloc(data_len + AES_BLOCK_SIZE);
    if (!result.encrypted_data) {
        free(result.iv);
        return result; // Memory allocation failed
    }

    // Perform encryption
    if (EVP_EncryptUpdate(ctx, result.encrypted_data, &len, data, data_len) != 1) {
        free(result.encrypted_data);
        free(result.iv);
        return result; // Encryption failed
    }
    ciphertext_len = len;

    // Finalize encryption
    if (EVP_EncryptFinal_ex(ctx, result.encrypted_data + len, &len) != 1) {
        free(result.encrypted_data);
        free(result.iv);
        return result; // Finalization failed
    }
    ciphertext_len += len;

    // Set the length of the encrypted data
    result.encrypted_len = ciphertext_len;

    // Store the key used for encryption
    result.key = (unsigned char*)malloc(key_len);
    if (result.key) {
        memcpy(result.key, key, key_len);
    }

    // Securely zero out the key after use
    memset((unsigned char*)key, 0, key_len);

    EVP_CIPHER_CTX_free(ctx);
    return result;
}