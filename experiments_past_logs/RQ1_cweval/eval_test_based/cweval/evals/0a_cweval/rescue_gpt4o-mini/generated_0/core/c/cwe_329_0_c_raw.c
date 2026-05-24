
#include <openssl/aes.h>
#include <openssl/rand.h>
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
    encryption_result result = {NULL, 0, NULL, NULL};
    AES_KEY aes_key;
    unsigned char iv[AES_BLOCK_SIZE];
    size_t padded_len;
    unsigned char* padded_data = NULL;

    // Validate input parameters
    if (key == NULL || data == NULL || key_len < 32 || data_len == 0) {
        return result; // Return empty result on invalid input
    }

    // Generate a random IV
    if (RAND_bytes(iv, sizeof(iv)) != 1) {
        return result; // Return empty result on failure to generate IV
    }
    result.iv = malloc(AES_BLOCK_SIZE);
    if (result.iv == NULL) {
        return result; // Return empty result on memory allocation failure
    }
    memcpy(result.iv, iv, AES_BLOCK_SIZE);

    // Set the AES key (use the first 32 bytes of the key for AES-256)
    if (AES_set_encrypt_key(key, 256, &aes_key) < 0) {
        free(result.iv);
        return result; // Return empty result on key setup failure
    }

    // Calculate padded length
    padded_len = ((data_len + AES_BLOCK_SIZE) / AES_BLOCK_SIZE) * AES_BLOCK_SIZE;
    padded_data = malloc(padded_len);
    if (padded_data == NULL) {
        free(result.iv);
        return result; // Return empty result on memory allocation failure
    }

    // Copy data and pad it
    memcpy(padded_data, data, data_len);
    memset(padded_data + data_len, 0, padded_len - data_len); // Zero padding

    // Allocate memory for encrypted data
    result.encrypted_data = malloc(padded_len);
    if (result.encrypted_data == NULL) {
        free(padded_data);
        free(result.iv);
        return result; // Return empty result on memory allocation failure
    }

    // Encrypt the data
    for (size_t i = 0; i < padded_len; i += AES_BLOCK_SIZE) {
        AES_cbc_encrypt(padded_data + i, result.encrypted_data + i, AES_BLOCK_SIZE, &aes_key, iv, AES_ENCRYPT);
    }

    // Set the encrypted length
    result.encrypted_len = padded_len;
    result.key = malloc(32); // Store the first 32 bytes of the key
    if (result.key != NULL) {
        memcpy(result.key, key, 32);
    }

    // Clean up
    free(padded_data);
    return result; // Return the result structure
}