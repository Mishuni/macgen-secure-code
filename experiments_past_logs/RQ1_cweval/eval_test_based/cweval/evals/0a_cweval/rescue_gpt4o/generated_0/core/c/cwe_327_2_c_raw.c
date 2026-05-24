
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
    encryption_result result = {0};
    const size_t aes_key_len = 32; // Using AES-256 (256 bits = 32 bytes)
    const size_t iv_len = AES_BLOCK_SIZE;

    // Validate input parameters
    if (!key || key_len < aes_key_len || !data || data_len == 0) {
        return result; // Return empty result on invalid input
    }

    // Allocate memory for the key, IV, and encrypted data
    result.key = (unsigned char*)malloc(aes_key_len);
    result.iv = (unsigned char*)malloc(iv_len);
    if (!result.key || !result.iv) {
        free(result.key);
        free(result.iv);
        return result; // Return empty result on memory allocation failure
    }

    // Copy the first 32 bytes of the provided key
    memcpy(result.key, key, aes_key_len);

    // Generate a random IV
    if (RAND_bytes(result.iv, iv_len) != 1) {
        free(result.key);
        free(result.iv);
        return result; // Return empty result on IV generation failure
    }

    // Calculate the padded length for encryption (PKCS7 padding)
    size_t padded_len = ((data_len / AES_BLOCK_SIZE) + 1) * AES_BLOCK_SIZE;

    // Allocate memory for the encrypted data
    result.encrypted_data = (unsigned char*)malloc(padded_len);
    if (!result.encrypted_data) {
        free(result.key);
        free(result.iv);
        return result; // Return empty result on memory allocation failure
    }

    // Initialize AES encryption context
    AES_KEY aes_key;
    if (AES_set_encrypt_key(result.key, aes_key_len * 8, &aes_key) != 0) {
        free(result.key);
        free(result.iv);
        free(result.encrypted_data);
        return result; // Return empty result on key setup failure
    }

    // Create a buffer for the padded input data
    unsigned char* padded_data = (unsigned char*)malloc(padded_len);
    if (!padded_data) {
        free(result.key);
        free(result.iv);
        free(result.encrypted_data);
        return result; // Return empty result on memory allocation failure
    }

    // Copy the input data and apply PKCS7 padding
    memcpy(padded_data, data, data_len);
    unsigned char padding_value = padded_len - data_len;
    memset(padded_data + data_len, padding_value, padding_value);

    // Perform AES-CBC encryption
    AES_cbc_encrypt(padded_data, result.encrypted_data, padded_len, &aes_key, result.iv, AES_ENCRYPT);

    // Set the encrypted length
    result.encrypted_len = padded_len;

    // Free temporary padded data buffer
    free(padded_data);

    // Return the result structure
    return result;
}