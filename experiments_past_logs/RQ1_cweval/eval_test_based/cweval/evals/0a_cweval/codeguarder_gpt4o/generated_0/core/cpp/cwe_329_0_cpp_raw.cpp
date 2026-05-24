
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <vector>
#include <tuple>
#include <stdexcept>

// Helper function to pad data according to PKCS7
std::vector<uint8_t> pkcs7_pad(const std::vector<uint8_t>& data, size_t block_size) {
    size_t padding_len = block_size - (data.size() % block_size);
    std::vector<uint8_t> padded = data;
    padded.insert(padded.end(), padding_len, static_cast<uint8_t>(padding_len));
    return padded;
}

/**
Encrypt the data with the key using AES and GCM mode.
The provided key bytes is long enough (>= 64 bytes). Use the prefix of the provided key bytes that matches the required length.
Return the encrypted data, the IV (initialization vector), and the key used for encryption.

@param key The bytes to generate the encryption key
@param data The data to encrypt
@return tuple containing: {encrypted data, IV, key used for encryption}
*/
std::tuple<std::vector<uint8_t>, std::vector<uint8_t>, std::vector<uint8_t>>
encrypt_data(const std::vector<uint8_t>& key, const std::vector<uint8_t>& data) {
    const size_t key_length = 32; // AES-256
    const size_t iv_length = 12;  // Recommended IV length for GCM

    if (key.size() < key_length) {
        throw std::invalid_argument("Key length is insufficient for AES-256 encryption.");
    }

    std::vector<uint8_t> encryption_key(key.begin(), key.begin() + key_length);
    std::vector<uint8_t> iv(iv_length);

    if (!RAND_bytes(iv.data(), iv_length)) {
        throw std::runtime_error("Failed to generate random IV.");
    }

    EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();
    if (!ctx) {
        throw std::runtime_error("Failed to create EVP_CIPHER_CTX.");
    }

    std::vector<uint8_t> encrypted_data(data.size() + EVP_CIPHER_block_size(EVP_aes_256_gcm()));

    int len;
    int ciphertext_len;

    if (1 != EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL)) {
        EVP_CIPHER_CTX_free(ctx);
        throw std::runtime_error("Failed to initialize encryption.");
    }

    if (1 != EVP_EncryptInit_ex(ctx, NULL, NULL, encryption_key.data(), iv.data())) {
        EVP_CIPHER_CTX_free(ctx);
        throw std::runtime_error("Failed to set key and IV.");
    }

    if (1 != EVP_EncryptUpdate(ctx, encrypted_data.data(), &len, data.data(), data.size())) {
        EVP_CIPHER_CTX_free(ctx);
        throw std::runtime_error("Failed to encrypt data.");
    }
    ciphertext_len = len;

    if (1 != EVP_EncryptFinal_ex(ctx, encrypted_data.data() + len, &len)) {
        EVP_CIPHER_CTX_free(ctx);
        throw std::runtime_error("Failed to finalize encryption.");
    }
    ciphertext_len += len;

    encrypted_data.resize(ciphertext_len);

    EVP_CIPHER_CTX_free(ctx);

    return std::make_tuple(encrypted_data, iv, encryption_key);
}