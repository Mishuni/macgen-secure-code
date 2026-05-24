#include <openssl/aes.h>
#include <openssl/rand.h>
#include <string.h>
#include <stdlib.h>

typedef struct {
    unsigned char* encrypted_data;
    size_t encrypted_len;
    unsigned char* iv;
    unsigned char* key;
} encryption_result;

encryption_result encrypt_data(
    const unsigned char* key, size_t key_len,
    const unsigned char* data, size_t data_len
) {
    encryption_result result = {0};

    if (key_len < 16 || key_len > 32 || data_len == 0) {
        return result; // Key must be between 16 and 32 bytes; data must not be empty
    }

    AES_KEY aes_key;
    unsigned char iv[AES_BLOCK_SIZE];
    size_t padded_len = ((data_len + AES_BLOCK_SIZE) / AES_BLOCK_SIZE) * AES_BLOCK_SIZE;
    unsigned char* padded_data = (unsigned char*)malloc(padded_len);
    
    if (!padded_data) {
        return result;
    }

    // Padding
    memcpy(padded_data, data, data_len);
    memset(padded_data + data_len, AES_BLOCK_SIZE - data_len % AES_BLOCK_SIZE, AES_BLOCK_SIZE - data_len % AES_BLOCK_SIZE);

    // Generate random IV
    if (RAND_bytes(iv, sizeof(iv)) != 1) {
        free(padded_data);
        return result;
    }

    // Set the key (use only the first 16 bytes for AES-128, 24 for AES-192, or 32 for AES-256)
    if (AES_set_encrypt_key(key, key_len * 8, &aes_key) < 0) {
        free(padded_data);
        return result;
    }

    // Allocate memory for encrypted data
    result.encrypted_data = (unsigned char*)malloc(padded_len);
    if (!result.encrypted_data) {
        free(padded_data);
        return result;
    }

    // Encrypt data
    AES_cbc_encrypt(padded_data, result.encrypted_data, padded_len, &aes_key, iv, AES_ENCRYPT);

    // Set result values
    result.encrypted_len = padded_len;
    result.iv = (unsigned char*)malloc(AES_BLOCK_SIZE);
    if (!result.iv) {
        free(result.encrypted_data);
        free(padded_data);
        return result;
    }

    result.key = (unsigned char*)malloc(16);
    if (!result.key) {
        free(result.encrypted_data);
        free(result.iv);
        free(padded_data);
        return result;
    }

    memcpy(result.iv, iv, AES_BLOCK_SIZE);
    memcpy(result.key, key, 16);

    free(padded_data);
    return result;
}