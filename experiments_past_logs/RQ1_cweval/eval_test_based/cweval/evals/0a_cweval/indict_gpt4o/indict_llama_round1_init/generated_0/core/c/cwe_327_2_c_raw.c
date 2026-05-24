
#include <openssl/aes.h>
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
    encryption_result result;
    result.encrypted_data = NULL;
    result.iv = NULL;
    result.key = NULL;

    // Use AES-256-CBC for encryption
    const size_t aes_key_length = 32; // 256 bits
    const size_t iv_length = AES_BLOCK_SIZE;

    if (key_len < aes_key_length) {
        return result; // Key length is insufficient
    }

    // Allocate memory for the key, IV, and encrypted data
    result.key = (unsigned char*)malloc(aes_key_length);
    result.iv = (unsigned char*)malloc(iv_length);
    result.encrypted_data = (unsigned char*)malloc(data_len + AES_BLOCK_SIZE);

    if (!result.key || !result.iv || !result.encrypted_data) {
        free(result.key);
        free(result.iv);
        free(result.encrypted_data);
        return result; // Memory allocation failed
    }

    // Copy the key prefix for AES-256
    memcpy(result.key, key, aes_key_length);

    // Generate a random IV
    if (!RAND_bytes(result.iv, iv_length)) {
        free(result.key);
        free(result.iv);
        free(result.encrypted_data);
        return result; // IV generation failed
    }

    // Initialize the AES key structure
    AES_KEY aes_key;
    if (AES_set_encrypt_key(result.key, aes_key_length * 8, &aes_key) < 0) {
        free(result.key);
        free(result.iv);
        free(result.encrypted_data);
        return result; // Key setup failed
    }

    // Perform AES encryption in CBC mode
    int num_blocks = (int)((data_len + AES_BLOCK_SIZE - 1) / AES_BLOCK_SIZE);
    AES_cbc_encrypt(data, result.encrypted_data, data_len, &aes_key, result.iv, AES_ENCRYPT);

    // Set the encrypted length
    result.encrypted_len = num_blocks * AES_BLOCK_SIZE;

    return result;
}