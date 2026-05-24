
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
@param key_len The length of the provided key bytes.
@param data The data to encrypt.
@param data_len The length of the data to encrypt.

@return The encrypted data, the IV, and the key used for encryption.
*/
encryption_result encrypt_data(
    const unsigned char* key, size_t key_len,
    const unsigned char* data, size_t data_len
) {
    encryption_result result = {0}; // Initialize the result structure to zero
    const size_t aes_key_len = 32; // AES-256 requires a 256-bit (32-byte) key
    unsigned char aes_key[aes_key_len];
    unsigned char iv[AES_BLOCK_SIZE];
    unsigned char* encrypted_data = NULL;
    size_t padded_len = 0;

    // Validate inputs
    if (!key || key_len < aes_key_len || !data || data_len == 0) {
        fprintf(stderr, "Invalid input parameters.\n");
        return result;
    }

    // Derive the AES key from the provided key bytes
    memcpy(aes_key, key, aes_key_len);

    // Generate a random IV
    if (!RAND_bytes(iv, AES_BLOCK_SIZE)) {
        fprintf(stderr, "Failed to generate random IV.\n");
        return result;
    }

    // Calculate the padded length (data_len rounded up to the nearest multiple of AES_BLOCK_SIZE)
    padded_len = ((data_len + AES_BLOCK_SIZE - 1) / AES_BLOCK_SIZE) * AES_BLOCK_SIZE;

    // Allocate memory for the encrypted data
    encrypted_data = (unsigned char*)malloc(padded_len);
    if (!encrypted_data) {
        fprintf(stderr, "Memory allocation failed for encrypted data.\n");
        return result;
    }
    memset(encrypted_data, 0, padded_len); // Initialize the buffer to zero

    // Initialize AES encryption context
    AES_KEY enc_key;
    if (AES_set_encrypt_key(aes_key, aes_key_len * 8, &enc_key) != 0) {
        fprintf(stderr, "Failed to set AES encryption key.\n");
        free(encrypted_data);
        return result;
    }

    // Perform AES-CBC encryption
    AES_cbc_encrypt(data, encrypted_data, padded_len, &enc_key, iv, AES_ENCRYPT);

    // Populate the result structure
    result.encrypted_data = encrypted_data;
    result.encrypted_len = padded_len;
    result.iv = (unsigned char*)malloc(AES_BLOCK_SIZE);
    result.key = (unsigned char*)malloc(aes_key_len);

    if (!result.iv || !result.key) {
        fprintf(stderr, "Memory allocation failed for IV or key.\n");
        free(encrypted_data);
        free(result.iv);
        free(result.key);
        return (encryption_result){0};
    }

    memcpy(result.iv, iv, AES_BLOCK_SIZE);
    memcpy(result.key, aes_key, aes_key_len);

    return result;
}