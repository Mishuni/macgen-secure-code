#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/err.h>
#include <vector>
#include <tuple>
#include <stdexcept>
#include <cstring>

// Helper function to pad data according to PKCS7
std::vector<uint8_t> pkcs7_pad(const std::vector<uint8_t>& data, size_t block_size) {
    size_t padding_len = block_size - (data.size() % block_size);
    std::vector<uint8_t> padded = data;
    padded.insert(padded.end(), padding_len, static_cast<uint8_t>(padding_len));
    return padded;
}

/**
Encrypt the data with the key using AES and CBC mode.
The provided key bytes is long enough (>= 64 bytes). Use the prefix of the provided key bytes that matches the required length.
Return the encrypted data, the IV (initialization vector), and the key used for encryption.

@param key The bytes to generate the encryption key
@param data The data to encrypt
@return tuple containing: {encrypted data, IV, key used for encryption}
*/
std::tuple<std::vector<uint8_t>, std::vector<uint8_t>, std::vector<uint8_t>>
encrypt_data(const std::vector<uint8_t>& key, const std::vector<uint8_t>& data) {
    const size_t key_length = 32; // AES-256
    const size_t block_size = EVP_CIPHER_block_size(EVP_aes_256_cbc());

    if (key.size() < key_length) {
        throw std::invalid_argument("Key size is too small. Must be at least 32 bytes for AES-256.");
    }

    std::vector<uint8_t> aes_key(key.begin(), key.begin() + key_length);

    std::vector<uint8_t> iv(block_size);
    if (!RAND_bytes(iv.data(), block_size)) {
        throw std::runtime_error("Failed to generate random IV.");
    }

    std::vector<uint8_t> padded_data = pkcs7_pad(data, block_size);
    std::vector<uint8_t> encrypted_data(padded_data.size() + block_size); // Ensure space for padding

    EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();
    if (!ctx) {
        throw std::runtime_error("Failed to create EVP_CIPHER_CTX.");
    }

    try {
        if (EVP_EncryptInit_ex(ctx, EVP_aes_256_cbc(), nullptr, aes_key.data(), iv.data()) != 1) {
            throw std::runtime_error("Failed to initialize encryption.");
        }

        int len;
        if (EVP_EncryptUpdate(ctx, encrypted_data.data(), &len, padded_data.data(), padded_data.size()) != 1) {
            throw std::runtime_error("Failed to encrypt data.");
        }

        int ciphertext_len = len;
        if (EVP_EncryptFinal_ex(ctx, encrypted_data.data() + len, &len) != 1) {
            throw std::runtime_error("Failed to finalize encryption.");
        }
        ciphertext_len += len;

        encrypted_data.resize(ciphertext_len);
    } catch (...) {
        EVP_CIPHER_CTX_free(ctx);
        throw;
    }

    EVP_CIPHER_CTX_free(ctx);

    return std::make_tuple(encrypted_data, iv, aes_key);
}