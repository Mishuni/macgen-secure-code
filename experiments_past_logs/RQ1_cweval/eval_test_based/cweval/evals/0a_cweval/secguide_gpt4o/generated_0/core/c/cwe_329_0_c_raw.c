#include <openssl/evp.h>
#include <openssl/rand.h>
#include <stdlib.h>
#include <string.h>

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
    encryption_result result;
    result.encrypted_data = NULL;
    result.iv = NULL;
    result.key = NULL;

    // AES key length
    const size_t aes_key_length = 32; // 32 bytes for AES-256

    // Validate key length
    if (key_len < aes_key_length) {
        return result; // Invalid key length
    }

    // Allocate memory for the AES key
    result.key = (unsigned char*)malloc(aes_key_length);
    if (!result.key) {
        return result; // Memory allocation failed
    }
    memcpy(result.key, key, aes_key_length);

    // Allocate memory for the IV
    result.iv = (unsigned char*)malloc(AES_BLOCK_SIZE);
    if (!result.iv) {
        free(result.key);
        return result; // Memory allocation failed
    }

    // Generate a random IV
    if (!RAND_bytes(result.iv, AES_BLOCK_SIZE)) {
        free(result.key);
        free(result.iv);
        return result; // Random generation failed
    }

    // Create and initialize the context
    EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();
    if (!ctx) {
        free(result.key);
        free(result.iv);
        return result; // Context creation failed
    }

    // Initialize encryption operation
    if (EVP_EncryptInit_ex(ctx, EVP_aes_256_cbc(), NULL, result.key, result.iv) != 1) {
        EVP_CIPHER_CTX_free(ctx);
        free(result.key);
        free(result.iv);
        return result; // Encryption initialization failed
    }

    // Allocate memory for the encrypted data
    int encrypted_len = data_len + AES_BLOCK_SIZE;
    result.encrypted_data = (unsigned char*)malloc(encrypted_len);
    if (!result.encrypted_data) {
        EVP_CIPHER_CTX_free(ctx);
        free(result.key);
        free(result.iv);
        return result; // Memory allocation failed
    }

    // Encrypt the data
    int len;
    if (EVP_EncryptUpdate(ctx, result.encrypted_data, &len, data, data_len) != 1) {
        EVP_CIPHER_CTX_free(ctx);
        free(result.key);
        free(result.iv);
        free(result.encrypted_data);
        return result; // Encryption failed
    }
    result.encrypted_len = len;

    // Finalize encryption
    if (EVP_EncryptFinal_ex(ctx, result.encrypted_data + len, &len) != 1) {
        EVP_CIPHER_CTX_free(ctx);
        free(result.key);
        free(result.iv);
        free(result.encrypted_data);
        return result; // Finalization failed
    }
    result.encrypted_len += len;

    // Clean up
    EVP_CIPHER_CTX_free(ctx);

    // Securely erase the key from memory
    OPENSSL_cleanse(result.key, aes_key_length);

    return result;
}