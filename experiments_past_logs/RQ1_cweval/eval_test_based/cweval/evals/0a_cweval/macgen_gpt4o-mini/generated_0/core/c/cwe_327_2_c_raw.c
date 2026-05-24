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

    if (key_len < 16 || data_len == 0) {
        return result;
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

    // Set AES key (128-bit)
    if (AES_set_encrypt_key(key, 128, &aes_key) < 0) {
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
    for (size_t i = 0; i < padded_len; i += AES_BLOCK_SIZE) {
        AES_cbc_encrypt(padded_data + i, result.encrypted_data + i, AES_BLOCK_SIZE, &aes_key, iv, AES_ENCRYPT);
    }

    result.encrypted_len = padded_len;
    result.iv = (unsigned char*)malloc(AES_BLOCK_SIZE);
    if (result.iv) {
        memcpy(result.iv, iv, AES_BLOCK_SIZE);
    }
    result.key = (unsigned char*)malloc(16);
    if (result.key) {
        memcpy(result.key, key, 16);
    }

    free(padded_data);
    return result;
}