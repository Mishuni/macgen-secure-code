
#include <openssl/aes.h>
#include <openssl/des.h>
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
    memset(&result, 0, sizeof(result)); // Initialize result structure

    // AES key length and block size
    const size_t AES_KEY_LENGTH = 16; // 128 bits
    const size_t AES_BLOCK_SIZE = AES_BLOCK_SIZE;

    // Allocate memory for IV
    result.iv = (unsigned char*)malloc(AES_BLOCK_SIZE);
    if (result.iv == NULL) {
        return result; // Return empty result on failure
    }

    // Generate a random IV
    if (RAND_bytes(result.iv, AES_BLOCK_SIZE) != 1) {
        free(result.iv);
        return result; // Return empty result on failure
    }

    // Calculate the length of the encrypted data
    size_t padded_len = ((data_len + AES_BLOCK_SIZE) / AES_BLOCK_SIZE) * AES_BLOCK_SIZE;
    result.encrypted_data = (unsigned char*)malloc(padded_len);
    if (result.encrypted_data == NULL) {
        free(result.iv);
        return result; // Return empty result on failure
    }

    // Prepare the AES key
    unsigned char aes_key[AES_KEY_LENGTH];
    memcpy(aes_key, key, AES_KEY_LENGTH); // Use the first 16 bytes of the key

    // Initialize AES encryption
    AES_KEY encrypt_key;
    if (AES_set_encrypt_key(aes_key, 128, &encrypt_key) < 0) {
        free(result.encrypted_data);
        free(result.iv);
        return result; // Return empty result on failure
    }

    // Perform AES encryption in CBC mode
    AES_cbc_encrypt(data, result.encrypted_data, data_len, &encrypt_key, result.iv, AES_ENCRYPT);

    result.encrypted_len = padded_len; // Set the length of the encrypted data
    result.key = aes_key; // Store the key used for encryption

    return result; // Return the result structure
}