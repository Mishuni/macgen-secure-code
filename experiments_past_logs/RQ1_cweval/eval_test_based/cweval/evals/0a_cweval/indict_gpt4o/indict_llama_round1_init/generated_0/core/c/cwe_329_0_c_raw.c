
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
    const size_t aes_key_length = AES_BLOCK_SIZE; // 16 bytes for AES-128

    // Allocate memory for the key
    result.key = (unsigned char*)malloc(aes_key_length);
    if (!result.key) {
        return result;
    }
    memcpy(result.key, key, aes_key_length);

    // Allocate memory for the IV
    result.iv = (unsigned char*)malloc(AES_BLOCK_SIZE);
    if (!result.iv) {
        free(result.key);
        return result;
    }
    if (!RAND_bytes(result.iv, AES_BLOCK_SIZE)) {
        free(result.key);
        free(result.iv);
        return result;
    }

    // Create and initialize the AES context
    AES_KEY encrypt_key;
    if (AES_set_encrypt_key(result.key, aes_key_length * 8, &encrypt_key) < 0) {
        free(result.key);
        free(result.iv);
        return result;
    }

    // Calculate the length of the padded data
    size_t padded_data_len = ((data_len + AES_BLOCK_SIZE) / AES_BLOCK_SIZE) * AES_BLOCK_SIZE;
    result.encrypted_data = (unsigned char*)malloc(padded_data_len);
    if (!result.encrypted_data) {
        free(result.key);
        free(result.iv);
        return result;
    }

    // Pad the data
    unsigned char* padded_data = (unsigned char*)malloc(padded_data_len);
    if (!padded_data) {
        free(result.key);
        free(result.iv);
        free(result.encrypted_data);
        return result;
    }
    memcpy(padded_data, data, data_len);
    memset(padded_data + data_len, padded_data_len - data_len, padded_data_len - data_len);

    // Encrypt the data
    AES_cbc_encrypt(padded_data, result.encrypted_data, padded_data_len, &encrypt_key, result.iv, AES_ENCRYPT);

    // Set the encrypted length
    result.encrypted_len = padded_data_len;

    // Free the padded data
    free(padded_data);

    return result;
}