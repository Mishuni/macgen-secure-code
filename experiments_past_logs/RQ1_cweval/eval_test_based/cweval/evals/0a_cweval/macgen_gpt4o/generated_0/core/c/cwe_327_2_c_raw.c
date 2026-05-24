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
    if (key_len < 16) return result;

    unsigned char aes_key[16];
    memcpy(aes_key, key, 16);

    result.iv = (unsigned char*)malloc(AES_BLOCK_SIZE);
    if (!result.iv) return result;
    if (!RAND_bytes(result.iv, AES_BLOCK_SIZE)) {
        free(result.iv);
        return result;
    }

    AES_KEY enc_key;
    if (AES_set_encrypt_key(aes_key, 128, &enc_key) < 0) {
        free(result.iv);
        return result;
    }

    size_t padded_len = ((data_len + AES_BLOCK_SIZE) / AES_BLOCK_SIZE) * AES_BLOCK_SIZE;
    result.encrypted_data = (unsigned char*)malloc(padded_len);
    if (!result.encrypted_data) {
        free(result.iv);
        return result;
    }

    unsigned char* padded_data = (unsigned char*)malloc(padded_len);
    if (!padded_data) {
        free(result.iv);
        free(result.encrypted_data);
        return result;
    }
    memcpy(padded_data, data, data_len);
    memset(padded_data + data_len, padded_len - data_len, padded_len - data_len);

    AES_cbc_encrypt(padded_data, result.encrypted_data, padded_len, &enc_key, result.iv, AES_ENCRYPT);

    result.encrypted_len = padded_len;
    result.key = (unsigned char*)malloc(16);
    if (!result.key) {
        free(result.iv);
        free(result.encrypted_data);
        free(padded_data);
        return result;
    }
    memcpy(result.key, aes_key, 16);

    free(padded_data);
    return result;
}