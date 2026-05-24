
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

    // Use AES-256-CBC for encryption
    const size_t aes_key_length = 32; // 256 bits
    const size_t iv_length = AES_BLOCK_SIZE;

    if (key_len < aes_key_length) {
        return result; // Key length is insufficient
    }

    // Calculate padding
    size_t padding_len = AES_BLOCK_SIZE - (data_len % AES_BLOCK_SIZE);
    size_t padded_data_len = data_len + padding_len;

    // Allocate memory for the key, IV, and encrypted data
    result.key = (unsigned char*)malloc(aes_key_length);
    result.iv = (unsigned char*)malloc(iv_length);
    result.encrypted_data = (unsigned char*)malloc(padded_data_len);

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

    // Create padded data
    unsigned char* padded_data = (unsigned char*)malloc(padded_data_len);
    if (!padded_data) {
        free(result.key);
        free(result.iv);
        free(result.encrypted_data);
        return result; // Memory allocation failed
    }
    memcpy(padded_data, data, data_len);
    memset(padded_data + data_len, padding_len, padding_len);

    // Perform AES encryption in CBC mode
    AES_cbc_encrypt(padded_data, result.encrypted_data, padded_data_len, &aes_key, result.iv, AES_ENCRYPT);

    // Set the encrypted length
    result.encrypted_len = padded_data_len;

    // Securely erase padded data
    memset(padded_data, 0, padded_data_len);
    free(padded_data);

    // Securely erase the AES key structure
    memset(&aes_key, 0, sizeof(AES_KEY));

    return result;
}