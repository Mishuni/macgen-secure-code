
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

    // Validate key length for AES-128, AES-192, and AES-256
    if (key_len < 16) {
        return result; // Key too short for AES-128
    }

    // Determine key length and set encryption key
    int key_bits = 128; // Default to AES-128
    if (key_len >= 32) {
        key_bits = 256; // Use AES-256 if key is long enough
    } else if (key_len >= 24) {
        key_bits = 192; // Use AES-192 if key is long enough
    }

    if (AES_set_encrypt_key(key, key_bits, &aes_key) < 0) {
        return result; // Key setting failed
    }

    // Handle zero-length input data
    if (data_len == 0) {
        result.encrypted_len = 0;
        result.iv = (unsigned char*)malloc(AES_BLOCK_SIZE);
        if (result.iv != NULL) {
            if (RAND_bytes(result.iv, AES_BLOCK_SIZE) != 1) {
                free(result.iv);
                result.iv = NULL;
            }
        }
        result.key = (unsigned char*)malloc(key_len);
        if (result.key != NULL) {
            memcpy(result.key, key, key_len);
        }
        return result;
    }

    // Calculate padded length
    size_t padded_len = ((data_len + AES_BLOCK_SIZE) / AES_BLOCK_SIZE) * AES_BLOCK_SIZE;

    // Allocate memory for the encrypted data
    result.encrypted_data = (unsigned char*)malloc(padded_len);
    if (result.encrypted_data == NULL) {
        return result; // Memory allocation failed
    }

    // Generate a random IV
    if (RAND_bytes(iv, sizeof(iv)) != 1) {
        free(result.encrypted_data);
        return result; // IV generation failed
    }

    // Perform the encryption
    AES_cbc_encrypt(data, result.encrypted_data, padded_len, &aes_key, iv, AES_ENCRYPT);

    // Set the result values
    result.encrypted_len = padded_len;
    result.iv = (unsigned char*)malloc(AES_BLOCK_SIZE);
    if (result.iv != NULL) {
        memcpy(result.iv, iv, AES_BLOCK_SIZE);
    }

    result.key = (unsigned char*)malloc(key_len);
    if (result.key != NULL) {
        memcpy(result.key, key, key_len); // Store the full key used for encryption
    }

    return result;
}