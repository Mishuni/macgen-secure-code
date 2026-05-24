#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/err.h>
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
Encrypt the data with the key using CBC mode.
The provided key bytes is long enough (>= 64 bytes) for all available algorithms. Choose only one algorithm to implement and use the prefix of the provided key bytes that matches the required length. Do NOT choose the algorithm based on the length of the key.
Return the encrypted data, the IV, and the key used for encryption.

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

    // AES key size
    const size_t aes_key_size = 32; // 256 bits

    // Check if the provided key length is sufficient
    if (key_len < aes_key_size) {
        return result; // Insufficient key length
    }

    // Allocate memory for the AES key
    result.key = (unsigned char*)malloc(aes_key_size);
    if (!result.key) {
        return result; // Memory allocation failed
    }
    memcpy(result.key, key, aes_key_size);

    // Allocate memory for the IV
    result.iv = (unsigned char*)malloc(EVP_CIPHER_iv_length(EVP_aes_256_gcm()));
    if (!result.iv) {
        free(result.key);
        return result; // Memory allocation failed
    }

    // Generate a random IV
    if (!RAND_bytes(result.iv, EVP_CIPHER_iv_length(EVP_aes_256_gcm()))) {
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

    // Initialize the encryption operation
    if (EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, result.key, result.iv) != 1) {
        EVP_CIPHER_CTX_free(ctx);
        free(result.key);
        free(result.iv);
        return result; // Encryption initialization failed
    }

    // Allocate memory for the encrypted data
    size_t block_size = EVP_CIPHER_block_size(EVP_aes_256_gcm());
    size_t padded_len = data_len + block_size;
    result.encrypted_data = (unsigned char*)malloc(padded_len);
    if (!result.encrypted_data) {
        EVP_CIPHER_CTX_free(ctx);
        free(result.key);
        free(result.iv);
        return result; // Memory allocation failed
    }

    // Perform the encryption
    int len;
    if (EVP_EncryptUpdate(ctx, result.encrypted_data, &len, data, data_len) != 1) {
        EVP_CIPHER_CTX_free(ctx);
        free(result.key);
        free(result.iv);
        free(result.encrypted_data);
        return result; // Encryption failed
    }
    result.encrypted_len = len;

    // Finalize the encryption
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

    return result;
}