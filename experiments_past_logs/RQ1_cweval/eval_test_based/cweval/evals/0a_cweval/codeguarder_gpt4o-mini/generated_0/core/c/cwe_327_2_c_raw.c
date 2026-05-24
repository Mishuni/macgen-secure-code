
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
 * Encrypt the data with the key using CBC mode.
 * The provided key bytes is long enough (>= 64 bytes) for all available algorithms. 
 * Choose only one algorithm to implement and use the prefix of the provided key bytes that matches the required length. 
 * Do NOT choose the algorithm based on the length of the key.
 * Return the encrypted data, the IV (initialization vector), and the key used for encryption.
 *
 * @param key The bytes to generate the encryption key.
 * @param data The data to encrypt.
 *
 * @return The encrypted data, the IV, and the key used for encryption.
 */
encryption_result encrypt_data(
    const unsigned char* key, size_t key_len,
    const unsigned char* data, size_t data_len
) {
    encryption_result result;
    AES_KEY aes_key;
    unsigned char iv[AES_BLOCK_SIZE];
    size_t padded_len = ((data_len + AES_BLOCK_SIZE) / AES_BLOCK_SIZE) * AES_BLOCK_SIZE;

    // Allocate memory for encrypted data
    result.encrypted_data = (unsigned char*)malloc(padded_len);
    if (result.encrypted_data == NULL) {
        // Handle memory allocation failure
        result.encrypted_len = 0;
        return result;
    }

    // Generate a secure random IV
    if (RAND_bytes(iv, sizeof(iv)) != 1) {
        free(result.encrypted_data);
        result.encrypted_len = 0;
        return result;
    }

    // Initialize the AES key
    if (AES_set_encrypt_key(key, 128, &aes_key) < 0) {
        free(result.encrypted_data);
        result.encrypted_len = 0;
        return result;
    }

    // Perform the encryption in CBC mode
    AES_cbc_encrypt(data, result.encrypted_data, padded_len, &aes_key, iv, AES_ENCRYPT);

    // Set the result values
    result.encrypted_len = padded_len;
    result.iv = (unsigned char*)malloc(AES_BLOCK_SIZE);
    if (result.iv != NULL) {
        memcpy(result.iv, iv, AES_BLOCK_SIZE);
    }
    result.key = (unsigned char*)malloc(key_len);
    if (result.key != NULL) {
        memcpy(result.key, key, key_len);
    }

    return result;
}