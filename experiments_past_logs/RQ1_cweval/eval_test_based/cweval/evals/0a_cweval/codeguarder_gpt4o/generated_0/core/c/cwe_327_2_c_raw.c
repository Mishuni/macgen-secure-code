
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <string.h>
#include <stdlib.h>

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
    encryption_result result = {NULL, 0, NULL, NULL};
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) return result;

    const EVP_CIPHER *cipher = EVP_aes_256_cbc();
    size_t iv_len = EVP_CIPHER_iv_length(cipher);
    size_t block_size = EVP_CIPHER_block_size(cipher);
    size_t enc_key_len = EVP_CIPHER_key_length(cipher);

    result.iv = (unsigned char*)malloc(iv_len);
    result.key = (unsigned char*)malloc(enc_key_len);
    if (!result.iv || !result.key) {
        EVP_CIPHER_CTX_free(ctx);
        return result;
    }

    if (!RAND_bytes(result.iv, iv_len)) {
        EVP_CIPHER_CTX_free(ctx);
        free(result.iv);
        free(result.key);
        return result;
    }

    memcpy(result.key, key, enc_key_len);

    if (EVP_EncryptInit_ex(ctx, cipher, NULL, result.key, result.iv) != 1) {
        EVP_CIPHER_CTX_free(ctx);
        free(result.iv);
        free(result.key);
        return result;
    }

    result.encrypted_data = (unsigned char*)malloc(data_len + block_size);
    if (!result.encrypted_data) {
        EVP_CIPHER_CTX_free(ctx);
        free(result.iv);
        free(result.key);
        return result;
    }

    int len;
    if (EVP_EncryptUpdate(ctx, result.encrypted_data, &len, data, data_len) != 1) {
        EVP_CIPHER_CTX_free(ctx);
        free(result.iv);
        free(result.key);
        free(result.encrypted_data);
        return result;
    }
    result.encrypted_len = len;

    if (EVP_EncryptFinal_ex(ctx, result.encrypted_data + len, &len) != 1) {
        EVP_CIPHER_CTX_free(ctx);
        free(result.iv);
        free(result.key);
        free(result.encrypted_data);
        return result;
    }
    result.encrypted_len += len;

    EVP_CIPHER_CTX_free(ctx);
    return result;
}