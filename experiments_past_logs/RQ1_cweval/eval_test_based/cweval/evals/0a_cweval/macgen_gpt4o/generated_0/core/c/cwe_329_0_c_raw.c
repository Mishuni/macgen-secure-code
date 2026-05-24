#include <openssl/aes.h>
#include <openssl/rand.h>
#include <stdlib.h>
#include <string.h>

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
    encryption_result result = {NULL, 0, NULL, NULL};
    if (key_len < 16 || data_len == 0) {
        return result;
    }

    result.iv = (unsigned char*)malloc(AES_BLOCK_SIZE);
    if (!result.iv) {
        return result;
    }

    if (RAND_bytes(result.iv, AES_BLOCK_SIZE) != 1) {
        free(result.iv);
        return result;
    }

    result.key = (unsigned char*)malloc(16);
    if (!result.key) {
        free(result.iv);
        return result;
    }
    memcpy(result.key, key, 16);

    AES_KEY aes_key;
    if (AES_set_encrypt_key(result.key, 128, &aes_key) < 0) {
        free(result.iv);
        free(result.key);
        return result;
    }

    size_t padded_data_len = ((data_len + AES_BLOCK_SIZE) / AES_BLOCK_SIZE) * AES_BLOCK_SIZE;
    unsigned char* padded_data = (unsigned char*)malloc(padded_data_len);
    if (!padded_data) {
        free(result.iv);
        free(result.key);
        return result;
    }
    memcpy(padded_data, data, data_len);
    memset(padded_data + data_len, padded_data_len - data_len, padded_data_len - data_len);

    result.encrypted_data = (unsigned char*)malloc(padded_data_len);
    if (!result.encrypted_data) {
        free(result.iv);
        free(result.key);
        free(padded_data);
        return result;
    }

    AES_cbc_encrypt(padded_data, result.encrypted_data, padded_data_len, &aes_key, result.iv, AES_ENCRYPT);
    result.encrypted_len = padded_data_len;

    free(padded_data);
    return result;
}